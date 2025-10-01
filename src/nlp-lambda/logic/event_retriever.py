from google import genai
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.database as database
import json
import numpy as np
import uuid
import anthropic
from datetime import datetime
import boto3
import common_utils.sqs as sqs


GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
genai_client = genai.Client(api_key=GOOGLE_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']
events_collection = db['events']

events_client = boto3.client('events')

def process_event(bill, event):
    def _get_embedding(content):
        result = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=content,
        config=genai.types.EmbedContentConfig(output_dimensionality=768))

        [embedding_obj] = result.embeddings
        embedding_values_np = np.array(embedding_obj.values)
        normed_embedding = embedding_values_np / np.linalg.norm(embedding_values_np)

        return normed_embedding.tolist()

    content = ' '.join(event['topics']) + ' ' + ' '.join(event['tags']) + ' ' + event['overview']

    event['embedding'] = _get_embedding(content)

    actions = bill['actions']

    if actions and len(actions) > 0:
        latest = actions[-1]
        latest_action = latest.get('text', None)
    else:
        latest_action = None

    # Add bill data to event
    event['bill'] = {
        'id': bill['bill_id'],
        'title': bill['title'],
        'date': bill['latest_action_date'],
        'latest_action': latest_action
    }

    # add id and status to event
    event['id'] = bill['bill_id'] + '-' + str(uuid.uuid4())
    event['status'] = bill.get('status', 'pending')

    return event

def process_batch_results(batch_id):
    """Process results from a completed batch - to be called separately when batch is done"""
    try:
        # Retrieve batch results
        batch = anthropic_client.messages.batches.retrieve(batch_id)
        
        if batch.processing_status != 'ended':
            return {
                'status': 'not_ready',
                'processing_status': batch.processing_status,
                'errored': batch.request_counts.errored,
                'succeeded': batch.request_counts.succeeded,
                'processing': batch.request_counts.processing,
                'cancelled': batch.request_counts.cancelled,
                'expired': batch.request_counts.expired,
                'message': f'Batch {batch_id} has {batch.request_counts.succeeded} succeeded requests, {batch.request_counts.errored} errored requests, {batch.request_counts.processing} processing requests, {batch.request_counts.cancelled} cancelled requests, {batch.request_counts.expired} expired requests.'
            }

        # Log batch processing time
        started_at = batch.created_at
        ended_at = batch.ended_at
        if started_at and ended_at:
            duration = (ended_at - started_at).total_seconds()
            print(f"Batch {batch_id} processing duration: {duration} seconds")
        
        processed_bills = []
        
        for result in anthropic_client.messages.batches.results(batch_id):
            bill_id = result.custom_id
            
            if result.result.type == 'succeeded':
                try:
                    # Parse the events from the response
                    events_json = result.result.message.content[0].text
                    events_json = '[' + events_json # Add opening bracket from prefill
                    events = json.loads(events_json)
                    
                    # Get bill from database
                    bill = database.get_bill(bills_collection, bill_id)
                    
                    if bill:
                        event_ids = []
                        for i, event in enumerate(events):
                            try:
                                event = process_event(bill, event)
                                success = database.insert_event(events_collection, event)
                            
                                if success:
                                    print(f"Inserted event id {event['id']} for bill {bill_id}")
                                    event_ids.append(event['id'])
                                else:
                                    print(f"Failed to insert event id {event['id']} for bill {bill_id}")
                            except Exception as e:
                                print(f"Error processing event {i}: {e}")
                                processed_bills.append({
                                    'bill_id': bill_id,
                                    'status': 'processing_error',
                                    'error': str(e)
                                })
                                break

                        # Update bill with events
                        bill['events'] = event_ids
                        success = database.update_bill(bills_collection, bill)
                        
                        if success:
                            print(f"Updated bill {bill_id} with {len(event_ids)} events")
                            processed_bills.append({
                                'bill_id': bill_id,
                                'status': 'success',
                                'events_count': len(event_ids)
                            })
                        else:
                            print(f"Failed to update bill {bill_id} with events")
                            processed_bills.append({
                                'bill_id': bill_id,
                                'status': 'database_update_failed'
                            })
                    else:
                        print(f"Bill {bill_id} not found in database")
                        processed_bills.append({
                            'bill_id': bill_id,
                            'status': 'bill_not_found'
                        })
                        
                except Exception as e:
                    print(f"Error processing events for bill {bill_id}: {str(e)}")
                    processed_bills.append({
                        'bill_id': bill_id,
                        'status': 'processing_error',
                        'error': str(e)
                    })
            else:
                print(f"Batch request failed for bill {bill_id}: {result.result.error}")
                processed_bills.append({
                    'bill_id': bill_id,
                    'status': 'api_error',
                    'error': str(result.result.error)
                })
        
        return {
            'status': 'completed',
            'batch_id': batch_id,
            'processed_bills': processed_bills,
            'total_processed': len(processed_bills)
        }
        
    except Exception as e:
        print(f"Error processing batch results for {batch_id}: {str(e)}")
        return {
            'status': 'error',
            'batch_id': batch_id,
            'error': str(e)
        }

def cleanup_eventbridge_rule(batch_id):
    """
    Clean up EventBridge rules for a completed or timed-out batch.
    """
    
    # Remove targets first
    events_client.remove_targets(
        Rule=f'batch-check-{batch_id}',
        Ids=[f'nlp-queue-target-{batch_id}']
    )
    
    # Delete the rule
    events_client.delete_rule(Name=f'batch-check-{batch_id}')

    print(f"Cleaned up EventBridge: batch-check-{batch_id}")

def main(batch_id, bill_ids):
    result = process_batch_results(batch_id)

    # If batch is completed, clean up all EventBridge rules, retry any failures
    if result.get('status') == 'completed':
        print(f"Batch {batch_id} completed successfully, cleaning up EventBridge rule")
        cleanup_eventbridge_rule(batch_id)

        retry = []
        for bill in result.get('processed_bills'):
            if bill.get('status') != 'success' and bill.get('status') != 'database_update_failed':
                
                print(f"Error processing bill {bill.get('bill_id')}: {bill.get('error', 'Unknown error')}. Retrying...")
                
                retry.append(bill.get('bill_id'))

        if retry:
            sqs.send_to_nlp_queue({
                "action": "e_event_extractor",
                "payload": {
                    "bill_ids": retry,
                    "type": "new_bill"
                }
            })
    # If batch is not completed, report status and wait
    elif result.get('status') == 'not_ready':
        print(result.get('message'))
    # If batch is errored or expired, clean up all rules and retry entire job
    elif result.get('status') == 'errored' or result.get('status') == 'expired':
        # Error occurred
        print(f"Error processing batch {batch_id}: {result.get('error', 'Unknown error')}")
        
        # Clean up all rules on error
        cleanup_eventbridge_rule(batch_id)
        
        # send batch again
        sqs.send_to_nlp_queue({
            "action": "e_event_extractor",
            "payload": {
                "bill_ids": bill_ids,
                "type": "new_bill"
            }
        })

def handler(payload):
    """Handle event retriever requests from EventBridge or direct calls"""
    batch_id = payload.get('batch_id')
    bill_ids = payload.get('bill_ids')
    
    print(f"Processing batch status check for {batch_id}")
    
    # Process the batch
    result = main(batch_id, bill_ids)

    print(result)

if __name__ == "__main__":
    # Example usage for batch processing
    payload = {
        "batch_id": "msgbatch_019rntWnPMD5M7dz53qJNT4u",
        "bill_ids": ["S2806-119"]
    }
    
    print(f"Processing batch event extraction for bills: {payload['bill_ids']}")
    
    handler(payload)
