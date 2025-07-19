import os
import boto3
import json

sqs = boto3.client('sqs')

CLUSTERER_QUEUE_URL = os.getenv("CLUSTERER_QUEUE_URL")
CONTENT_QUEUE_URL = os.getenv("CONTENT_QUEUE_URL")
print(f"Auxiom Queue URL is {CLUSTERER_QUEUE_URL}")

def send_to_clusterer_queue(message):

    response = sqs.send_message(
        QueueUrl=CLUSTERER_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

def send_to_content_queue(message):

    response = sqs.send_message(
        QueueUrl=CONTENT_QUEUE_URL,
        MessageBody=json.dumps(message)
    )