import os
import requests
import logging
import json
import datetime
import boto3

from logic.article_resource import ArticleResource

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Congress Documents Integration
class Congress(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.api_key = os.environ.get('CONGRESS_API_KEY')
        self.headers = {"Content-Type": "application/json"}

        self.today = datetime.datetime.now()  # Current date
        self.time_constraint = datetime.datetime.now() - datetime.timedelta(days=7)  # 7 days ago

    def get_bills(self):
        """
        Fetch recent bills from the Congress API and return all bills without filtering.
        
        Returns:
            list: List of dicts with bill info
        """
        try:
            seen_titles = set()
            
            # Build URL - get all recent bills without search query since API search is broken
            if self.time_constraint:
                from_date = self.time_constraint.strftime('%Y-%m-%dT%H:%M:%SZ')
                to_date = self.today.strftime('%Y-%m-%dT%H:%M:%SZ')
                url = (f"https://api.congress.gov/v3/bill/119?"
                       f"fromDateTime={from_date}"
                       f"&toDateTime={to_date}"
                       f"&api_key={self.api_key}")
            else:
                # Get all available bills without time constraints
                url = f"https://api.congress.gov/v3/bill/119?api_key={self.api_key}"

            try:
                print(f"Fetching bills from Congress API: {url}")
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    bills = data.get('bills', [])
                    print(f"Retrieved {len(bills)} bills from Congress API")

                    if not bills:
                        print("No bills found from Congress API")
                        return None

                    # Process all bills
                    all_bills = []
                    for bill in bills:
                        title = bill.get('title', '')

                        # Simple exact duplicate check without fuzzy matching
                        if title:
                            title_normalized = title.lower().strip()
                            if title_normalized in seen_titles:
                                print(f"Skipping duplicate bill: {title}")
                                continue
                            seen_titles.add(title_normalized)

                        congress_num = bill.get('congress')
                        bill_type = bill.get('type', '').lower()
                        bill_number = bill.get('number')

                        bill_identifier = None
                        if congress_num and bill_type and bill_number:
                            # Example: "hr3876-119"
                            bill_identifier = f"{bill_type}{bill_number}-{congress_num}"
                        
                        # Generate public Congress.gov URL instead of API URL
                        bill_url = ''
                        if congress_num and bill_type and bill_number:
                            # Convert API bill type to public URL format
                            url_type_map = {
                                'hr': 'house-bill',
                                's': 'senate-bill', 
                                'hjres': 'house-joint-resolution',
                                'sjres': 'senate-joint-resolution',
                                'hconres': 'house-concurrent-resolution',
                                'sconres': 'senate-concurrent-resolution',
                                'hres': 'house-resolution',
                                'sres': 'senate-resolution'
                            }
                            url_bill_type = url_type_map.get(bill_type.lower(), bill_type)
                            bill_url = f"https://www.congress.gov/bill/{congress_num}th-congress/{url_bill_type}/{bill_number}"
                        
                        latest_action = bill.get('latestAction', {})
                        latest_action_date = latest_action.get('actionDate', '')
                        latest_action_text = latest_action.get('text', '')
                        
                        all_bills.append({
                            "title": title,
                            "bill_id": bill_identifier,
                            "url": bill_url,
                            "latest_action_date": latest_action_date,
                            "latest_action_text": latest_action_text,
                            "congress": congress_num,
                            "bill_type": bill_type,
                            "bill_number": bill_number
                        })
                        
                    print(f"Processed {len(all_bills)} unique bills")
                    
                    # Return all bills without filtering
                    if all_bills:
                        print(f"Successfully retrieved {len(all_bills)} bills.")
                        for i, bill in enumerate(all_bills[:5]):  # Show first 5 bills
                            print(f"  {i+1}. {bill['title'][:60]}...")
                        return all_bills
                    else:
                        print("No bills found.")
                        return None
                        
                else:
                    print(f"Congress API request failed. Status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as req_err:
                print(f"Network or request error: {req_err}")
                return None
            except json.JSONDecodeError as json_err:
                print(f"JSON decoding error: {json_err}. Response: {response.text}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred processing Congress API query: {e}")
                return None

        except Exception as e:
            print(f"Error in Congress integration's get_bills method: {e}")
            return None
    
    
def save_to_database(bills):
    """
    Save congress bills to PostgreSQL database without embeddings.
    Clears existing bills first to ensure fresh data with correct URLs.
    Embeddings will be generated later by the clusterer stack.
    
    Args:
        bills: List of bill dictionaries
    """
    import psycopg2
    
    db_access_url = os.environ.get('DB_ACCESS_URL')
    if not db_access_url:
        raise ValueError("DB_ACCESS_URL environment variable not set")
    
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        # Clear existing congress bills to ensure fresh data with correct URLs
        cursor.execute("DELETE FROM congress_bills")
        deleted_count = cursor.rowcount
        conn.commit()  # COMMIT THE DELETE IMMEDIATELY
        print(f"Cleared {deleted_count} existing congress bills from database")
        
        saved_count = 0
        
        # Process all bills
        for bill in bills:
            try:
                # Create a placeholder embedding (will be updated by clusterer)
                placeholder_embedding = f"[{','.join(['0'] * 384)}]"
                
                # Insert bill into database without real embedding
                cursor.execute("""
                    INSERT INTO congress_bills (
                        bill_id, title, url, latest_action_date, latest_action_text,
                        congress, bill_type, bill_number, embedding
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (bill_id) DO NOTHING
                """, (
                    bill['bill_id'],
                    bill['title'],
                    bill.get('url'),
                    bill.get('latest_action_date'),
                    bill.get('latest_action_text'),
                    bill.get('congress'),
                    bill.get('bill_type'),
                    bill.get('bill_number'),
                    placeholder_embedding
                ))
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving bill {bill.get('bill_id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        print(f"Successfully saved {saved_count} new bills to database")
        print("Note: Embeddings will be generated by the clusterer stack")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        print(f"Unexpected error saving to database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def handler(payload):
    """
    AWS Lambda handler function to process incoming events for Congress bills.
    """
    topics = payload.get("topics")
    if not topics:
        print("No topics provided in the payload.")

    print(f"congress_scraper invoked with topics: {topics}")
    congress = Congress(topics)
    bills = congress.get_bills()

    if bills is not None:
        print(f"Retrieved {len(bills)} congress bills.")
        
        # Save bills to PostgreSQL database
        print(f"Saving congress bills to PostgreSQL database")
        save_to_database(bills)
        
        # Send message to clusterer queue to generate embeddings
        try:
            sqs = boto3.client('sqs')
            clusterer_queue_url = os.environ.get('CLUSTERER_QUEUE_URL')
            
            if clusterer_queue_url:
                embed_message = {
                    "action": "e_embed_bills",
                    "payload": {}
                }
                
                response = sqs.send_message(
                    QueueUrl=clusterer_queue_url,
                    MessageBody=json.dumps(embed_message)
                )
                
                print(f"Sent embedding generation request to clusterer queue: {response.get('MessageId')}")
            else:
                print("Warning: CLUSTERER_QUEUE_URL not set, cannot trigger embedding generation")
                
        except Exception as e:
            print(f"Error sending message to clusterer queue: {e}")
        
        # Log bill details
        print(f"\n--- All Bills ({len(bills)} total) ---")
        for entry in bills[:5]:  # Show first 5 bills
            print(f"Title: {entry['title']}")
            print(f"Bill ID: {entry['bill_id']}") 
            print(f"URL: {entry['url']}")
            print(f"Latest Action Date: {entry['latest_action_date']}")
            print(f"Latest Action Text: {entry['latest_action_text'][:100]}...")
            print("--------------------")
    else:
        print("No bills found.")

if __name__ == "__main__":
    if os.environ.get('CONGRESS_API_KEY'):
        keywords = ["Trade", "Energy","Cybersecurity","Technology", "Economics", "Voting", "International Relations"] 
        
        # Test get_bills() method directly
        print("--- Testing get_bills() method directly ---")
        congress = Congress(keywords)
        bills_result = congress.get_bills()
        print("get_bills() returned:")
        print(bills_result)
        
        # Test handler function
        payload = {"topics": keywords}
        print("\n--- Invoking handler with example keywords ---")
        handler(payload)
    else:
        print("CONGRESS_API_KEY environment variable not set. Please set it to run the example.")
