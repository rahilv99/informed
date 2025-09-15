import os
import boto3
import json

sqs = boto3.client('sqs')

CLUSTERER_QUEUE_URL = os.getenv("CLUSTERER_QUEUE_URL")
CONTENT_QUEUE_URL = os.getenv("CONTENT_QUEUE_URL")
SCRAPER_QUEUE_URL = os.getenv("SCRAPER_QUEUE_URL")

def send_to_clusterer_queue(message):

    response = sqs.send_message(
        QueueUrl=CLUSTERER_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    if response.get('MessageId'):
        print(f"Message sent to scraper queue with ID: {response['MessageId']}")
    else:
        print("Failed to send message to scraper queue.")

def send_to_content_queue(message):

    response = sqs.send_message(
        QueueUrl=CONTENT_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    if response.get('MessageId'):
        print(f"Message sent to scraper queue with ID: {response['MessageId']}")
    else:
        print("Failed to send message to scraper queue.")

def send_to_scraper_queue(message):
    
    response = sqs.send_message(
        QueueUrl=SCRAPER_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    if response.get('MessageId'):
        print(f"Message sent to scraper queue with ID: {response['MessageId']}")
    else:
        print("Failed to send message to scraper queue.")