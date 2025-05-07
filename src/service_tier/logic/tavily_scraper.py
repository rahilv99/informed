"""
Tavily API scraping functionality to get article metadata
"""
import logging
import pandas as pd
from tavily import TavilyClient
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
DEFAULT_ARTICLE_AGE = 7
MAX_RETRIES = 10
BASE_DELAY = 0.33
MAX_DELAY = 15

from logic.article_resource import ArticleResource
from urllib.parse import urlparse

class TavilyScraper(ArticleResource):
    """
    Tavily Scraper class that retrieves news article headlines, URL, and metadata.
    """
    def __init__(self, user_topics_output, api_key=None):
        super().__init__(user_topics_output)
        self.logger = logging.getLogger('pulse.tavily')
        self.fuzzy_threshold = 87
        # Set Tavily parameters
        self.api_key = os.environ.get("TAVILY_API_KEY") if api_key is None else api_key
        self.max_results = 20  # Limit results per query for cost right now
    
    def get_articles(self):
        """
        Search for news articles related to user topics using Tavily API and store metadata in a DataFrame.
        """
        self.logger.info("Starting Tavily article retrieval")
    
        try:
            # Set up Tavily client
            client = TavilyClient(self.api_key)
            
            results = []
            
            # Process each user topic
            for topic in self.user_input:
                try:
                    self.logger.info(f"Searching for news articles related to: {topic}")
                    
                    # Get news articles from Tavily
                    response = self.fetch_with_retry(
                        client.search,
                        query=topic,
                        max_results=self.max_results,
                        time_range="week"
                    )
                    
                    articles = response.get("results", [])
                    self.logger.info(f"Found {len(articles)} articles for topic: {topic}")
                    
                    # Process each article
                    seen_titles = []
                    for article in articles:
                        # Extract article information
                        title = article.get("title", "No title")
                        url = article.get("url", "")
                        content = article.get("content", "")
                        
                        # Extract publisher from URL in a more robust way
                        try:
                            parsed_url = urlparse(url)
                            domain = parsed_url.netloc
                            # Remove www. and any subdomains before the main domain
                            parts = domain.split('.')
                            if len(parts) > 2:
                                if parts[0] == 'www':
                                    publisher = '.'.join(parts[1:])
                                else:
                                    # Try to extract main domain for sites like news.bbc.co.uk
                                    if len(parts) >= 3 and parts[-3] in ['co', 'com']:
                                        publisher = '.'.join(parts[-3:])
                                    else:
                                        publisher = '.'.join(parts[-2:])
                            else:
                                publisher = domain.replace('www.', '')
                            
                            # Clean up publisher name
                            publisher = publisher.split('.')[0].capitalize()
                        except Exception as e:
                            self.logger.warning(f"Error extracting publisher from URL {url}: {e}")
                            publisher = url.split("//")[-1].split("/")[0].replace("www.", "")

                        if self._is_duplicate_title(title, seen_titles):
                            self.logger.info(f"Skipping duplicate article: {title}")
                            continue

                        # Add article to results
                        results.append({
                            "title": title,
                            "url": url,
                            "content": content,
                            "publisher": publisher,
                            "source": "Tavily",
                            "keyword": topic
                        })

                        seen_titles.append(title.lower().strip())
                        
                except Exception as e:
                    self.logger.error(f"Error processing Tavily query for {topic}: {e}")
            
            # Create DataFrame and save to CSV
            if results:
                self.logger.info(f"Retrieved {len(results)} Tavily articles in total")
                df = pd.DataFrame(results)
                df.drop_duplicates(subset=['title'], inplace=True)
                return df
            else:
                self.logger.warning("No Tavily articles found matching the search criteria")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in Tavily integration: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example keywords
    keywords = ['Ukraine', 'Defense spending', 'Military']
    
    # Create scraper instance with your API key
    scraper = TavilyScraper(keywords)
    
    # Get articles and save to CSV
    df = scraper.get_articles()
    if df is not None:
        df.to_csv('tavily_articles.csv', index=False)