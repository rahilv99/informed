import os
import requests
import logging
import boto3
import json
import hashlib
from article_resource import ArticleResource
from botocore.exceptions import ClientError

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Government Documents Integration
class Gov(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        # In production, this should be moved to environment variables
        self.api_key = os.environ.get('GOVINFO_API_KEY')
        self.fuzzy_threshold = 95
        self.search_url = f"https://api.govinfo.gov/search?api_key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}
        self.logger = logging.getLogger('pulse.gov')

    def get_articles(self):
        try:
            results = []

            seen_titles = set()
            for topic in self.user_input:
                # Create payload for API request with date range for last week
                payload = {
                    "query": f"{topic} lastModified:range({self.time_constraint.strftime('%Y-%m-%d')}T12:00:05Z,)",
                    "pageSize": 20,
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
                    self.logger.info(f"Searching for government documents related to: {topic}")
                    response = self.fetch_with_retry(
                        requests.post, 
                        self.search_url, 
                        json=payload, 
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.logger.info(f"Found {len(data.get('results', []))} documents for topic: {topic}")
                        
                        if len(data.get('results', [])) == 0:
                            self.logger.warning(f"No documents found for topic: {topic}")
                            continue

                        for item in data.get("results", []):
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
                                continue
                                
                            # Trash articles recognizing some BS - makeshift filter
                            if 'recognizing' in item.get('title','').lower():
                                self.logger.info(f"Skipping document: {item.get('title','')} ({doc_type})")
                                continue
                                
                            title = item.get('title', '')
                            if 'v.' in title.lower():
                                self.logger.info(f"Skipping court document: {title} ({doc_type})")
                                continue

                            if self._is_duplicate_title(title, seen_titles):
                                self.logger.info(f"Skipping duplicate article: {title}")
                                continue

                                
                            url_with_key = f"{url}?api_key={self.api_key}"
                            full_text = self.get_document_text(url_with_key)

                            if len(full_text) < 5000:
                                self.logger.info(f"Skipping document with insufficient text: {title} ({len(full_text)} characters)")
                                continue
                            
                            date = item.get('dateIngested', '')
                            self.logger.info(f"Retrieved document: {title} ({len(full_text)} characters) from {url_with_key}")

                            results.append({
                                "title": title,
                                "url": url_with_key,
                                "keyword": topic,
                                "full_text": full_text,
                                "date": date
                            })

                            seen_titles.add(title.lower().strip())
                    else:
                        self.logger.error(f"API request failed with status code: {response.status_code}")
                except Exception as e:
                    self.logger.error(f"Error processing GovInfo query for {topic}: {e}")

            # Create DataFrame and normalize to match expected format
            if results:
                self.logger.info(f"Retrieved {len(results)} government documents in total")
                self.articles_df = results
            else:
                self.logger.warning("No government documents found matching the search criteria")

        except Exception as e:
            self.logger.error(f"Error in Gov integration: {e}")

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
    gov = Gov(topics)  # Add Gov instance

    # Retrieve articles from all sources
    gov.get_articles()  # Get government articles

    ans = gov.articles_df
    
    if ans is not None and len(ans) > 0:
        topics_str = json.dumps(topics, sort_keys=True)
        topics_hash = hashlib.sha256(topics_str.encode('utf-8')).hexdigest()

        save_to_s3(ans, topics_hash)

if __name__ == "__main__":
    topics = ["tariffs", "immigration", "foreign aid"]
    gov = Gov(topics)  # Add Gov instance

    # Retrieve articles from all sources
    gov.get_articles()  # Get government articles

    final_df = gov.articles_df