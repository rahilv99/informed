#!/usr/bin/env python3

from congress import CongressGovAPI, Bill
import database
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import sys
import json

# Replace with your actual API key
API_KEY = os.environ.get("CONGRESS_API_KEY", '7NxXpjZniUGLLvbeCp1q0bOVEitgvfZwl4zym9iE')
uri = "mongodb+srv://admin:astrapodcast!@auxiom-backend.7edkill.mongodb.net/?retryWrites=true&w=majority&appName=auxiom-backend"

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
    
    results = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    print(f"Processing {len(requery_objects)} requery items...")
    
    for requery_item in requery_objects:
        try:
            bill_id = requery_item['bill_id']
            field = requery_item['request']
            endpoint = requery_item['endpoint']
            
            print(f"\nProcessing requery for bill {bill_id} (request: {field})")
            
            # Get existing bill from database
            existing_bill = database.get_bill(bills_collection, bill_id)
            if not existing_bill:
                print(f"Warning: Bill {bill_id} not found in database. Skipping.")
                results["failed"] += 1
                results["errors"].append(f"Bill {bill_id} not found in database")
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
                        success = database.update_bill(bills_collection, bill_id, update_data)
                        
                        if success:
                            results["success"] += 1
                            print(f"Updated database for bill {bill_id}")
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to update database for bill {bill_id}")
                    else:
                        print(f"No text available for bill {bill_id} - may still be pending")
                        results["failed"] += 1
                        results["errors"].append(f"No text available for bill {bill_id}")
                        
                except Exception as text_error:
                    print(f"Error fetching text for bill {bill_id}: {text_error}")
                    results["failed"] += 1
                    results["errors"].append(f"Error fetching text for bill {bill_id}: {str(text_error)}")
            else:
                print(f"Unsupported request type: {field}")
                results["failed"] += 1
                results["errors"].append(f"Unsupported field type: {field}")
                
        except Exception as e:
            print(f"Error processing requery item: {e}")
            results["failed"] += 1
            results["errors"].append(f"Error processing requery item: {str(e)}")
        
        results["processed"] += 1
    
    # Close database connection
    client.close()
    
    print(f"\nRequery processing complete:")
    print(f"  Processed: {results['processed']}")
    print(f"  Successful: {results['success']}")
    print(f"  Failed: {results['failed']}")
    
    if results["errors"]:
        print(f"  Errors encountered:")
        for error in results["errors"]:
            print(f"    - {error}")
    
    return results


def handler(payload):
    """
    AWS Lambda handler function.
    """
    try:
        requery_objects = payload.get('requery_objects', [])
        return process_requery_items(requery_objects)
    except Exception as e:
        return {
            "success": False,
            "error": f"Lambda handler error: {str(e)}"
        }

if __name__ == "__main__":
    requery_objects = [
        {
            'bill_id': 'HR1234-118',
            'request': 'text',
            'endpoint': 'bill/118/hr/1234/text'
        }
    ]
    
    result = process_requery_items(requery_objects)
