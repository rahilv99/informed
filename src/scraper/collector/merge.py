import boto3
import json
import pandas as pd
from typing import List, Dict
import os
import pickle

bucket_name = os.getenv("BUCKET_NAME")
astra_bucket_name = os.getenv("ASTRA_BUCKET_NAME")


def read_json_from_s3(bucket_name: str, prefix: str) -> List[Dict]:
    """
    Read and combine all JSON files from S3 bucket into a single list of dictionaries
    """
    # Initialize S3 client
    s3 = boto3.client('s3')
    all_articles = []

    # List all objects in the folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Check if any contents exist
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if not key.endswith('/'):  # Skip folders
                try:
                    # Get the file content
                    file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                    content = file_obj['Body'].read().decode('utf-8')
                    
                    # Parse JSON array
                    articles = json.loads(content)
                    if isinstance(articles, list):
                        all_articles.extend(articles)
                    
                except Exception as e:
                    print(f"Error processing file {key}: {str(e)}")
                    continue

    return all_articles

def handler(payload):
    # Read all JSON files and combine them
    prefix = payload.get('prefix', 'gnews/')
    articles = read_json_from_s3(bucket_name, prefix)

    if not articles:
        print("No articles found in the bucket")
        return

    # Create DataFrame
    df = pd.DataFrame(articles)

    # Basic data info
    print(f"Total number of articles: {len(df)}")
    print("\nDataFrame Info:")
    print(df.info())

    # Serialize output
    serialized_data = pickle.dumps(df)
    key = f"{prefix}articles.pkl"
    # Upload to S3
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=astra_bucket_name, Key=key, Body=serialized_data)
        print('Saved serialized data')
    except Exception as e:
        print(f"Error saving to bucket {e}")
    
    next_event = {
        "action": "e_clean",
        "payload": {
            "prefix": prefix
        }
    }

    sqs = boto3.client('sqs')
    SCRAPER_QUEUE_URL = os.getenv("SCRAPER_QUEUE_URL")
    
    response = sqs.send_message(
        QueueUrl=SCRAPER_QUEUE_URL,
        MessageBody=json.dumps(next_event)
    )
    print(f"Sent message to SQS: {response.get('MessageId')}")