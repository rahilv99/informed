#!/usr/bin/env python3

from definitions.api import CongressGovAPI
from definitions.congress import Bill
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.s3 as s3
import common_utils.database as database


# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY", '7NxXpjZniUGLLvbeCp1q0bOVEitgvfZwl4zym9iE')
uri = os.environ.get("DB_URI", "mongodb+srv://admin:astrapodcast!@auxiom-backend.7edkill.mongodb.net/?retryWrites=true&w=majority&appName=auxiom-backend")

def process_requery_items(requery_objects):
    """
    Process a list of requery objects to fetch missing bill text.
    
    Args:
        requery_objects: List of dictionaries with 'bill_id', 'request', and 'endpoint'
    
    Returns:
        dict: Summary of processing results
    """
    
    # Initialize API client and database connection
    api = CongressGovAPI(API_KEY)
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['auxiom_database']
    bills_collection = db['bills']
    
    # Test database connection
    if not database.test_connection(client):
        print("Failed to connect to MongoDB. Exiting.")
        return {"success": False, "error": "Database connection failed"}
    

    updated = []
    errors = 0
    
    print(f"Processing {len(requery_objects)} requery items...")
    
    for requery_item in requery_objects:
        try:
            bill_id = requery_item['bill_id']
            field = requery_item['request']

            print(f"\nProcessing requery for bill {bill_id} (request: {field})")
            
            # Get existing bill from database
            existing_bill = database.get_bill(bills_collection, bill_id)
            if not existing_bill:
                print(f"Warning: Bill {bill_id} not found in database. Removing from requery.")
                updated.append(bill_id)
                continue
            
            # Create a Bill object with existing data
            bill_data = existing_bill.copy()
            bill_data['type'] = bill_data['bill_type']
            bill_data['number'] = bill_data['bill_number']
            
            bill = Bill(api, bill_data)
            
            # Attempt to fetch the text
            if field == 'text':
                try:
                    text = bill.get_text()
                    if text and len(text) > 0:
                        print(f"Successfully retrieved {len(text)} characters of text for bill {bill_id}")
                        
                        # Update the database with the new text
                        update_data = {"text": text}
                        success = database.update_bill(bills_collection, update_data)
                        
                        if success:
                            updated.append(bill_id)
                            print(f"Updated database for bill {bill_id}")
                        else:
                            errors += 1
                    else:
                        print(f"No text available for bill {bill_id} - do not delete object")
                        
                except Exception as text_error:
                    print(f"Error fetching text for bill {bill_id}: {text_error}")
                    errors += 1
            else:
                print(f"Unsupported request type: {field}")
                errors += 1
                
        except Exception as e:
            print(f"Error processing requery item: {e}")
            errors += 1
    
    # Delete successfully processed requery items from S3
    for bill_id in updated:
        s3.delete_json('requery', bill_id)
    
    # Close database connection
    client.close()
    
    print(f"\nRequery processing complete:")
    print(f"  Successful: {len(updated)}")
    for error in range(errors):
        print(f"Logging error {error}")
    
    return updated

def handler(payload):
    """
    AWS Lambda handler function.
    """
    requery_objects = s3.restore_dir('requery')
    updated = process_requery_items(requery_objects)

    # send updates as new bills
    for id in updated:
        update = {
            'action': 'extractor',
            'document_id': id,
            'type': 'new_bill'
        }

        # sqs.send_to_nlp_queue(update)

if __name__ == "__main__":
    requery_objects = [
        {
            'bill_id': 'HR1234-118',
            'request': 'text',
            'endpoint': 'bill/118/hr/1234/text'
        }
    ]
    
    process_requery_items(requery_objects)
