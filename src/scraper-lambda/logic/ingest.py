from definitions.api import CongressGovAPI
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import logic.database as database
import common_utils.s3 as s3
import common_utils.sqs as sqs

# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY", '7NxXpjZniUGLLvbeCp1q0bOVEitgvfZwl4zym9iE')
uri = os.environ.get("DB_URI", "mongodb+srv://admin:astrapodcast!@auxiom-backend.7edkill.mongodb.net/?retryWrites=true&w=majority&appName=auxiom-backend")

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

        print(f"Retrieved {len(bills)} bills updated in the last 2 days.")

        updates = []
        requery = []
        for i, bill in enumerate(bills):
            try:
                # Check if bill is already in database
                bill_id = bill.get_id()
                existing_bill = database.get_bill(bills_collection, bill_id)

                print(f"Bill ID: {bill_id}, Title: {bill.get_title()}, Latest Action: {bill.get_latest_action_date()}")

                # Get all information about this bill
                text = bill.get_text()
                print(f"{len(text)} characters of text extracted from the bill.")

                subjects = bill.get_subjects()
                print(f"Subjects: {subjects}")

                # Convert bill to dictionary with all information
                bill_data = bill.to_dict()

                if existing_bill:
                    # Bill exists - update it in the database
                    print(f"Bill {bill_id} already exists. Updating...")
                    success = database.update_bill(bills_collection, bill_data)

                    if success:
                        if len(text) == 0:
                            print("Warning: Text not yet available for this bill. Adding to requery queue.")
                            requery.append({
                                'bill_id': bill_id,
                                'request': 'text'
                            })
                        else:
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
                        if len(text) == 0:
                            print("Warning: Text not yet available for this bill. Adding to requery queue.")
                            requery.append({
                                'bill_id': bill_id,
                                'request': 'text'
                            })
                        else:
                            update_item = {
                                'action': 'extractor',
                                'document_id': bill_id,
                                'type': 'new_bill'
                            }
                            updates.append(update_item)

            except Exception as e:
                print(f"Error getting information for bill {i}: {e}")


        print(f"Processed {len(updates)} bill updates and added {len(requery)} new requery items.")

        return updates, requery

def handler(payload):
    updates, requeries = main()

    # save requeries
    for requery in requeries:
        s3.save_serialized('requery', requery['bill_id'], requery)
    
    print(f"Saved {len(requeries)} requery items to S3.")

    # send updates to SQS directly
    # for update in updates:
    #     sqs.send_to_nlp_queue(update)




if __name__ == "__main__":
    updates, requeries = main()

    # save requeries
    for requery in requeries:
        s3.save_serialized('requery', requery['bill_id'], requery)
    
    print(f"Saved {len(requeries)} requery items to S3.")

    # send updates to SQS directly
    for update in updates:
        sqs.send_to_scraper_queue(update)
