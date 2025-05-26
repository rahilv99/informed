import boto3
import json
from botocore.exceptions import ClientError
import logging
import os

QUEUE_URL = os.getenv("PUPPET_QUEUE_URL")


def handler():
    """
    Main Lambda handler to dispatch messages to SQS.
    
    """
    print("Starting the dispatch process to SQS queue.")

    topics = ["tariffs", "immigration", "foreign aid"]
    
    sqs = boto3.client('sqs')
    
    for topic in topics:
        try:
            response = sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps({'topics': [topic]})
            )
            print(f"Message sent successfully: {response['MessageId']}")
            
        except ClientError as e:
            error_info = {
                'topic': topic,
                'error': str(e)
            }
            print(f"Failed to send message: {error_info}")
            
    print(f"Dispatched {len(topics)} messages to SQS queue: {QUEUE_URL}")
    
    return {
        "statusCode": 200,
        "body": "Topics dispatched successfully"
    }