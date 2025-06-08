"""
Google News RSS scraping functionality to get article metadata
"""
import logging
from gnews import GNews
import json
import os
import boto3
from botocore.exceptions import ClientError
from article_resource import ArticleResource
import hashlib

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class GoogleNewsScraper(ArticleResource):
    """
    Google News Scraper class that retrieves news article headlines, URL, and metadata.
    """
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.logger = logging.getLogger('pulse.gnews') 
        # Set up GNews parameters
        self.period = '7d'  # Default to 7 days
        self.fuzzy_threshold = 87
        self.language = 'en'
        self.country = 'US'
        self.max_results = 75  # Limit results to avoid excessive processing
    
    def get_articles(self):
        """
        Search for news articles related to user topics and store metadata in a DataFrame.
        """
        self.logger.info("Starting Google News article retrieval")
    
        try:
            # Set up GNews
            gnews = GNews(
                language=self.language,
                country=self.country,
                period=self.period,
                max_results=self.max_results
            )
            
            results = []
            
            # Process each user topic
            seen_titles = set()
            for topic in self.user_input:
                try:
                    self.logger.info(f"Searching for news articles related to: {topic}")
                    
                    # Get news articles from Google News
                    news_results = self.fetch_with_retry(gnews.get_news, topic)
                    
                    self.logger.info(f"Found {len(news_results)} articles for topic: {topic}")
                    
                    # Process each article
                    for article in news_results:
                        # Extract article information
                        title = article.get("title", "No title")
                        url = article.get("url", "")
                        publisher = article.get("publisher", {}).get("title", "Unknown")

                        if self._is_duplicate_title(title, seen_titles):
                            self.logger.info(f"Skipping duplicate article: {title}")
                            continue

                        # Add article to results
                        results.append({
                            "title": title,
                            "url": url,
                            "publisher": publisher,
                            "keyword": topic
                        })

                        seen_titles.add(title.lower().strip())
                        
                except Exception as e:
                    self.logger.error(f"Error processing Google News query for {topic}: {e}")
            
            # Create DataFrame and save to CSV
            if results:
                self.logger.info(f"Retrieved {len(results)} gnewsernment documents in total")
                self.articles_df = results
            else:
                self.logger.warning("No Google News articles found matching the search criteria")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in Google News integration: {e}")
            return None


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
    filename = f"gnews/articles_{hash_key[:10]}.json"
    
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
    gnews = GoogleNewsScraper(topics)
    # Retrieve articles from all sources
    gnews.get_articles()  # Get gnewsernment articles

    ans = gnews.articles_df
    
    if ans is not None and len(ans) > 0:
        topics_str = json.dumps(topics, sort_keys=True)
        topics_hash = hashlib.sha256(topics_str.encode('utf-8')).hexdigest()

        save_to_s3(ans, topics_hash)

if __name__ == "__main__":
    topics = ["tariffs", "immigration", "foreign aid"]

    gnews = GoogleNewsScraper(topics)

    # Retrieve articles from all sources
    gnews.get_articles()  # Get gnewsernment articles

    final_df = gnews.articles_df