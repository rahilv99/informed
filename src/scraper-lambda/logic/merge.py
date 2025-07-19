import boto3
import json
import pandas as pd
from typing import List, Dict
import os
import pickle
from fuzzywuzzy import fuzz


bucket_name = os.getenv("BUCKET_NAME")
astra_bucket_name = os.getenv("ASTRA_BUCKET_NAME")


def read_json_from_s3(bucket_name: str, prefix: str) -> List[Dict]:
    """
    Read and combine all JSON files from S3 bucket into a single list of dictionaries
    """
    # Initialize S3 client
    s3 = boto3.client('s3')
    all_articles = []
    all_titles = set()

    if 'gnews/' in prefix:
        threshold = 87
    else:
        threshold = 90

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
                        for article in articles:
                            title = article.get('title', '').strip()
                            if not title:
                                continue
                            # Check for duplicates
                            if not is_duplicate_title(title, all_titles, threshold):
                                all_articles.append(article)
                                all_titles.add(title.lower())
                    
                except Exception as e:
                    print(f"Error processing file {key}: {str(e)}")
                    continue

    return all_articles

def is_duplicate_title(new_title, seen_titles, fuzzy_threshold=95):
        if not new_title or not seen_titles:
            return False

        # Normalize the new title
        new_title = new_title.lower().strip()

        # Check for exact match first (faster)
        if new_title in seen_titles:
            return True

        # Check for fuzzy matches
        for seen_title in seen_titles:
            # Use token sort ratio to handle word order differences
            ratio = fuzz.token_sort_ratio(new_title, seen_title)
            if ratio >= fuzzy_threshold:
                print(f"Fuzzy match found: '{new_title}' matches '{seen_title}' with ratio {ratio}")
                return True

        return False

def handler(payload):
    # Read all JSON files and combine them
    for prefix in ['gnews/', 'gov/']:
        articles = read_json_from_s3(bucket_name, prefix)

        if not articles:
            print("No articles found in the bucket")
            return
        
        # Create DataFrame
        df = pd.DataFrame(articles)

        # Print info after deduplication
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
        print(f"Sent clean request to Scraper SQS: {response.get('MessageId')}")

    next_event = {
        "action": "e_embed"
    }

    sqs = boto3.client('sqs')
    CLUSTERER_QUEUE_URL = os.getenv("CLUSTERER_QUEUE_URL")
    
    response = sqs.send_message(
        QueueUrl=CLUSTERER_QUEUE_URL,
        MessageBody=json.dumps(next_event)
    )
    print(f"Sent embedding request to Astra SQS: {response.get('MessageId')}")