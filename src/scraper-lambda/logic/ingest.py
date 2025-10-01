from definitions.api import CongressGovAPI
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.database as database
import common_utils.sqs as sqs
from datetime import datetime

# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY")
uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']

api = CongressGovAPI(API_KEY)

def main():
        bills = []
        offset = 0
        while True:
            page = api.get_bills(date_since_days=1, congress=119, offset=offset)
            bills.extend(page)
            if len(page) < 250: # last page
                print("Last page reached.")
                break
            offset += 250
            print("Fetching next page...")

        print(f"Retrieved {len(bills)} bills updated in the last 1 day.")

        updates = []
        revisions = []
        propogates = []
        seen = set()
        for i, bill in enumerate(bills):
            try:
                # Not historical bills
                published_date = bill.get_published_date()
                if published_date and datetime.strptime(published_date, '%Y-%m-%d').year <= 2022:
                    continue
                    
                # Check if bill is already in database
                bill_id = bill.get_id()

                if bill_id in seen:
                    continue

                existing_bill = database.get_bill(bills_collection, bill_id)

                print(f"Bill ID: {bill_id}, Title: {bill.get_title()}, Latest Action: {bill.get_latest_action_date()}")

                # Get all information about this bill
                text = bill.get_text()
                print(f"{len(text)} characters of text extracted from the bill.")

                # Skip bills with no text
                if len(text) == 0:
                    print(f"Skipping bill {bill_id} - no text available.")
                    continue

                subjects = bill.get_subjects()
                print(f"Subjects: {subjects}")

                # Convert bill to dictionary with all information
                bill_data = bill.to_dict()

                # TODO: issue with update / recognizing seen bills
                if existing_bill:
                    # Bill exists - update it in the database
                    print(f"Bill {bill_id} already exists. Updating...")

                    success = database.update_bill(bills_collection, bill_data)

                    if success:
                        # First time seeing this bill's text
                        if len(existing_bill['text']) == 0:
                            updates.append(bill_id)
                        # Significant revision has been made
                        elif abs(len(existing_bill['text']) - len(text)) > 1000:
                            revisions.append(bill_id)
                        # No updates, just new action
                        elif existing_bill['latest_action_date'] != bill_data['latest_action_date']:
                            propogates.append({'bill_id': bill_id, 'latest_action': bill['actions'][-1], 'date': bill_data['latest_action_date'], 'status': bill_data['status']})
                        # Otherwise don't bother updating
                        else:
                            print(f"Insignificant changes made to bill {bill_id}")
                    else:
                        print(f"No changes made to bill {bill_id}")
                else:
                    # Bill doesn't exist - insert as new
                    print(f"Bill {bill_id} is new. Inserting...")
                    success = database.insert_bill(bills_collection, bill_data)
                    
                    if success:
                        updates.append(bill_id)
                
                seen.add(bill_id)

            except Exception as e:
                print(f"Error getting information for bill {i}: {e}")


        print(f"Processed {len(updates)} new bills, {len(revisions)} bill revisions, and {len(propogates)} bill propogates.")

        return updates, revisions, propogates

def handler(payload):
    updates, revisions, propogates = main()
    # send updates to SQS directly

    if updates:
        update_item = {
            'action': 'e_event_extractor',
            'payload': {
                'ids': updates,
                'type': 'new_bill'
            }
        }
        sqs.send_to_nlp_queue(update_item)

    if revisions:
        revision_item = {
            'action': 'e_event_extractor',
            'payload': {
                'ids': revisions,
                'type': 'updated_bill'
            }
        }
        sqs.send_to_nlp_queue(revision_item)

    for item in propogates:
        bill_id = item['bill_id']
        # update all events for this bill
        data = {
            'bill': {
                'latest_action': item['latest_action'],
                'date': item['date']
            },
            'status': item['status']
        }
        database.update_events(bills_collection, bill_id, data)


if __name__ == "__main__":
    updates = main()

    # send updates to SQS directly
    sqs.send_to_nlp_queue(updates)
