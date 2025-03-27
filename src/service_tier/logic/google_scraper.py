import logging
import time
import pandas as pd
import datetime
from bs4 import BeautifulSoup
import requests

from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from gnews import GNews

class GoogleNews(ArticleResource):
    """
    Google News integration class that extends ArticleResource.
    
    This class uses Selenium to scrape news articles from Google News,
    follow redirects to original sources, extract content, and rank articles
    based on relevance to user input.
    """
    
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.logger = logging.getLogger('pulse.gnews')
        
        # Set up GNews parameters
        self.period = '7d'  # Default to 7 days, matching DEFAULT_ARTICLE_AGE
        self.language = 'en'
        self.country = 'US'
        self.max_results = 5  # Limit results to avoid excessive processing
        
        # Selenium parameters
        self.headless = True
        self.timeout = 10
        self.driver = None
    
    def setup_webdriver(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            
            # Disable images to speed up loading
            chrome_prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # 2 = block images
                    "notifications": 2,  # 2 = block notifications
                    "auto_select_certificate": 2,  # 2 = block certificate selection
                }
            }
            chrome_options.add_experimental_option("prefs", chrome_prefs)
            
            # Install ChromeDriver and set up the service
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            return True
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            return False
    
    def get_articles(self):
        """
        Search for news articles related to user topics and store them in a DataFrame.
        
        This method follows the pattern of other ArticleResource subclasses.
        """
        self.logger.info(f"Setting up WebDriver for article retrieval.")
    
        try:
            # Set up GNews
            gnews = GNews(
                language=self.language,
                country=self.country,
                period=self.period,
                max_results=self.max_results
            )
            
            # Set up WebDriver
            if not self.setup_webdriver():
                self.logger.error("Failed to set up WebDriver. Cannot proceed with article retrieval.")
                return
            
            results = []
            
            # Process each user topic
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
                        published_date = article.get("published date", "Unknown date")
                 
                        self.logger.info(f"Processing article: {title[:50]}...")
                        
                        # Get the final URL after redirects and extract content
                        original_url = self.get_final_url(url)
                        full_text = self.get_document_text_fast(original_url)
                        
                        # Skip articles with insufficient content
                        if len(full_text) < 1000:
                            self.logger.info(f"Skipping article with insufficient content: {title[:50]}")
                            continue
                        
                        # Add article to results
                        results.append({
                            "title": title,
                            "text": full_text,
                            "url": original_url,
                            "publisher": publisher,
                            "published_date": published_date
                        })
                        
                except Exception as e:
                    self.logger.error(f"Error processing Google News query for {topic}: {e}")
            
            # Create DataFrame and normalize to match expected format
            if results:
                self.logger.info(f"Retrieved {len(results)} Google News articles in total")
                self.articles_df = pd.DataFrame(results)
                self.normalize_df()
            else:
                self.logger.warning("No Google News articles found matching the search criteria")
                
        except Exception as e:
            self.logger.error(f"Error in Google News integration: {e}")
        finally:
            # Close the WebDriver
            if self.driver:
                self.driver.quit()
    
    def get_final_url(self, google_url: str) -> str:
        """
        Follow redirects and get the final URL of a news article.
        
        Args:
            google_url: The Google News URL to follow
            
        Returns:
            The final URL after all redirects
        """
        if not self.driver:
            self.logger.warning("WebDriver not initialized. Returning original URL.")
            return google_url
            
        try:
            # Load the Google News page
            self.driver.get(google_url)
            
            initial_url = google_url
            timeout = 3  # Timeout after 3 seconds
            start_time = time.time()

            # Polling mechanism to monitor redirect
            while True:
                current_url = self.driver.current_url
                if current_url != initial_url:
                    return current_url  # URL has changed

                if time.time() - start_time > timeout:
                    self.logger.warning("Timeout reached while waiting for URL to change.")
                    break

                time.sleep(0.2)  # Check every 0.2 seconds

            return current_url  # Return the current URL if timeout occurs
            
        except Exception as e:
            self.logger.error(f"Error following URL {google_url}: {e}")
            return google_url
    
    def get_document_text(self, url: str) -> str:
        """
        Extract text content from a document URL.
        
        NOTE: Could use requests library instead, faster but less robust
        
        Args:
            url: The URL to extract text from
            
        Returns:
            The extracted text content
        """
        if not self.driver:
            self.logger.warning("WebDriver not initialized. Returning empty string.")
            return ""
            
        try:
            self.logger.info(f"Loading document: {url}")
            # Load the page with Selenium
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(2)
            
            # Get the page source
            html_content = self.driver.page_source
            
            # Extract text from HTML
            return self._extract_text_from_html(html_content)
            
        except Exception as e:
            self.logger.error(f"Error retrieving document: {e}")
            return f"Error retrieving document: {e}"
    
    def get_document_text_fast(self, url: str) -> str:
        try:
            response = self.fetch_with_retry(requests.get, url)
            
            if response.status_code == 200:
                return self._extract_text_from_html(response.text)
            else:
                self.logger.error(f"Failed to retrieve document: {response.status_code}")
                return f"Failed to retrieve document: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Error retrieving document: {e}")
            return f"Error retrieving document: {e}"

    def _extract_text_from_html(self, html_content: str) -> str:
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text: break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            self.logger.info(f"Successfully extracted text from HTML ({len(text)} characters)")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from HTML: {e}")
            return html_content  # Return original content as fallback


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example keywords
    keywords = ['Ukraine', 'Defense spending', 'Military']
    
    # Create Gnews instance
    gnews = Gnews(keywords)
    
    # Get articles
    gnews.get_articles()
    
    # Rank articles
    gnews.rank_data()
    
    # Print results
    if not gnews.articles_df.empty:
        print(f"Found {len(gnews.articles_df)} articles")
        print(gnews.articles_df[['title', 'url', 'score']].head())
    else:
        print("No articles found")
