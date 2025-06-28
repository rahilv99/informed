import os
import requests
import logging
import json
import boto3
import hashlib
from botocore.exceptions import ClientError
import datetime


from article_resource import ArticleResource

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Government Documents Integration
class Gov(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.fuzzy_threshold = 95
        # In production, this should be moved to environment variables
        self.api_key = os.environ.get('GOVINFO_API_KEY')
        self.search_url = f"https://api.govinfo.gov/search?api_key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}

        self.today = datetime.date.today()
        self.time_constraint = self.today - datetime.timedelta(days=7)

    def get_articles(self):
        try:
            results = []
            seen_titles = set()  # Track titles for fuzzy matching
            for topic in self.user_input:
                # Create payload for API request with date range for last week
                payload = {
                    "query": f"{topic} publishdate:range({self.time_constraint.strftime('%Y-%m-%d')},{self.today.strftime('%Y-%m-%d')})",
                    "pageSize": 30,
                    "offsetMark": "*",
                    "sorts": [
                        {
                            "field": "score",
                            "sortOrder": "DESC"
                        }
                    ],
                    "historical": True,
                    "resultLevel": "default"
                }
                
                # Make API request with retry mechanism for resilience
                try:
                    print(f"Searching for government documents related to: {topic}")
                    response = self.fetch_with_retry(
                        requests.post, 
                        self.search_url, 
                        json=payload, 
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Found {len(data.get('results', []))} documents for topic: {topic}")
                        
                        if len(data.get('results', [])) == 0:
                            print(f"No documents found for topic: {topic}")
                            continue

                        for i, item in enumerate(data.get("results", [])):
                            print(f"Processing document: {i + 1}/{len(data['results'])} for topic: {topic}")
                            links = item.get("download", {})
                            url = None
                            
                            if 'pdfLink' in links:
                                url = links['pdfLink']
                                doc_type = 'pdf'
                            elif 'txtLink' in links:
                                url = links['txtLink']
                                doc_type = 'txt'
                            elif 'modsLink' in links:
                                url = links['modsLink']
                                doc_type = 'mods'
                            else:
                                print(f"No downloadable link found for document: {item.get('title','')}")
                                continue
                                
                            # Trash articles recognizing some BS - makeshift filter
                            if 'recognizing' in item.get('title','').lower():
                                print(f"Skipping document: {item.get('title','')} ({doc_type})")
                                continue
                                
                            # Check for duplicate titles using fuzzy matching
                            title = item.get('title', '')
                            if self._is_duplicate_title(title, seen_titles):
                                print(f"Skipping duplicate document: {title}")
                                continue
                                
                            if 'v.' in title.lower():
                                print(f"Skipping court document: {title} ({doc_type})")
                                continue
                                
                            url_with_key = f"{url}?api_key={self.api_key}"
                            full_text = self.get_document_text(url_with_key)

                            if len(full_text) < 4000:
                                print(f"Skipping document with insufficient text length: {title} ({len(full_text)} characters)")
                                continue
                            
                            print(f"Retrieved document: {title} ({len(full_text)} characters) from {url_with_key}")

                            # Add title to seen titles after processing
                            seen_titles.add(title.lower().strip())
                            
                            results.append({
                                "title": title,
                                "text": full_text,
                                "url": url_with_key,
                                "keyword": topic
                            })
                    else:
                        print(f"API request failed with status code: {response.status_code}")
                except Exception as e:
                    print(f"Error processing GovInfo query for {topic}: {e}")
                
            # Create DataFrame and normalize to match expected format
            if results:
                print(f"Retrieved {len(results)} government documents in total")
                df = results
                return df
            else:
                print("No government documents found matching the search criteria")
                return None
                
        except Exception as e:
            print(f"Error in Gov integration: {e}")



def save_to_s3(articles, hash_key):
    """
    Save articles to S3.
    
    Args:
        articles: List or dict of articles to save
    """
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    # Create filename with path
    filename = f"gov/articles_{hash_key[:10]}.json"
    
    # Prepare upload parameters
    params = {
        'Bucket': os.getenv('BUCKET_NAME'),
        'Key': filename,
        'Body': json.dumps(articles),
        'ContentType': 'application/json'
    }

    try:
        print(f"Saving articles to S3: {filename}")
        s3_client.put_object(**params)
        print('Successfully saved articles to S3')
    except ClientError as e:
        print(f"Error saving to S3: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def handler(payload):
    """
    AWS Lambda handler function to process incoming events.
    """
    topics = payload.get("topics")
    print("legal_scraper invoked with topics: ", topics)
    gov = Gov(topics)  # Add Gov instance

    # Retrieve articles from all sources
    df = gov.get_articles()  # Get government articles

    print(f"Retrieved {len(df)} government articles")
    
    if df is not None and len(df) > 0:
        topics_str = json.dumps(topics, sort_keys=True)
        topics_hash = hashlib.sha256(topics_str.encode('utf-8')).hexdigest()

        print(f"Saving {len(df)} government articles to S3 with hash: {topics_hash}")
        save_to_s3(df, topics_hash)

if __name__ == "__main__":
    keywords = ['tariffs']
    gov = Gov(keywords)  # Add Gov instance

    # Retrieve articles from all sources
    df = gov.get_articles()  # Get government articles

    for entry in df:
        print(f"Title: {entry['title']}")
        print(f"Text: {entry['text'][1000:1050]}")
        print(f"URL: {entry['url']}")
        print(f"Keyword: {entry['keyword']}")
        print("--------------------")