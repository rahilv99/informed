import boto3
import json
from botocore.exceptions import ClientError
import os
import psycopg2

PUPPET_QUEUE_URL = os.getenv("PUPPET_QUEUE_URL")
SCRAPER_QUEUE_URL = os.getenv("SCRAPER_QUEUE_URL")

DB_ACCESS_URL = os.getenv('DB_ACCESS_URL')

def get_unique_keywords(conn):
    """
    Fetch all unique keywords from users table
    
    Args:
        conn: psycopg2 connection object
    
    Returns:
        list: List of unique keywords
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_unique_keywords()")
            keywords = [row[0] for row in cur.fetchall()]
            return keywords
    except psycopg2.Error as e:
        print(f"Error fetching keywords: {e}")
        return []

def handler(payload):
    """
    Main Lambda handler to dispatch messages to SQS.
    
    """
    print("Starting the dispatch process to SQS queue.")

    conn = psycopg2.connect(DB_ACCESS_URL)
    topics = get_unique_keywords(conn)
    conn.close()
    
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