from definitions.api import CongressGovAPI
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.database as database
import common_utils.sqs as sqs

# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY")
uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']

api = CongressGovAPI(API_KEY)

def main():
        # Test database connection first
        if not database.test_connection(client):
            print("Failed to connect to MongoDB. Exiting.")
            return

        # The get_bills method now returns a list of Bill objects directly
        bills = api.get_bills(date_since_days=1)

        print(f"Retrieved {len(bills)} bills updated in the last 1 day.")

        updates = []
        seen = set()
        for i, bill in enumerate(bills):
            try:
                # Check if bill is already in database
                bill_id = bill.get_id()
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
                if existing_bill or bill_id in seen:
                    # Bill exists - update it in the database
                    print(f"Bill {bill_id} already exists. Updating...")

                    success = database.update_bill(bills_collection, bill_data)

                    if success:
                        # Add to updates list as an update
                        update_item = {
                            'action': 'extractor',
                            'latest_action': bill.get_latest_action(),
                            'bill_id': bill_id,
                            'type': 'new_action'
                        }
                        updates.append(update_item)
                else:
                    # Bill doesn't exist - insert as new
                    print(f"Bill {bill_id} is new. Inserting...")
                    success = database.insert_bill(bills_collection, bill_data)
                    
                    if success:
                        update_item = {
                            'action': 'extractor',
                            'document_id': bill_id,
                            'type': 'new_bill'
                        }
                        updates.append(update_item)
                
                seen.add(bill_id)

            except Exception as e:
                print(f"Error getting information for bill {i}: {e}")


        print(f"Processed {len(updates)} bill updates.")

        return updates

def handler(payload):
    updates = main()
    # send updates to SQS directly
    # sqs.send_to_nlp_queue(updates)


if __name__ == "__main__":
    updates = main()

    # send updates to SQS directly
    sqs.send_to_nlp_queue(updates)
