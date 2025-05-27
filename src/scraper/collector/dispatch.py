import boto3
import json
from botocore.exceptions import ClientError
import logging
import os

PUPPET_QUEUE_URL = os.getenv("PUPPET_QUEUE_URL")
SCRAPER_QUEUE_URL = os.getenv("SCRAPER_QUEUE_URL")


def handler(payload):
    """
    Main Lambda handler to dispatch messages to SQS.
    
    """
    print("Starting the dispatch process to SQS queue.")

    topics = ["tariffs", "immigration", "foreign aid"]
    
    sqs = boto3.client('sqs')
    
    for topic in topics:
        try:
            response = sqs.send_message(
                QueueUrl=PUPPET_QUEUE_URL,
                MessageBody=json.dumps({'topics': [topic]})
            )
            print(f"Message sent successfully: {response['MessageId']}")
            
        except ClientError as e:
            error_info = {
                'topic': topic,
                'error': str(e)
            }
            print(f"Failed to send message in PUPPET_QUEUE_URL: {error_info}")
        
        try:
            response = sqs.send_message(
                QueueUrl=SCRAPER_QUEUE_URL,
                MessageBody=json.dumps(
                    {
                        'action': 'e_gov',
                        "payload": {
                            'topics': [topic]
                        }
                    })
            )
            print(f"Message sent successfully: {response['MessageId']}")
            
        except ClientError as e:
            error_info = {
                'topic': topic,
                'error': str(e)
            }
            print(f"Failed to send message in SCRAPER_QUEUE_URL: {error_info}")
            
    print(f"Dispatched {len(topics)} messages")
    
    return {
        "statusCode": 200,
        "body": "Topics dispatched successfully"
    }