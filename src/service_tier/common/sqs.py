import os
import boto3
import json

sqs = boto3.client('sqs')

ASTRA_QUEUE_URL = os.getenv("ASTRA_QUEUE_URL")
print(f"Auxiom Queue URL is {ASTRA_QUEUE_URL}")

def send_to_sqs(message):
    """
    Send a message to the SQS queue
    """
    response = sqs.send_message(
        QueueUrl=ASTRA_QUEUE_URL,
        MessageBody=json.dumps(message)
    )