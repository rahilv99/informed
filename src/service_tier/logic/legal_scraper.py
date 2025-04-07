import pandas as pd
import os
import requests
import logging

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
        self.logger = logging.getLogger('pulse.gov')

    def get_articles(self):
        try:
            results = []
            seen_titles = []  # Track titles for fuzzy matching
            for topic in self.user_input:
                # Create payload for API request with date range for last week
                payload = {
                    "query": f"{topic} publishdate:range({self.time_constraint.strftime('%Y-%m-%d')},{self.today.strftime('%Y-%m-%d')})",
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
                                
                            # Check for duplicate titles using fuzzy matching
                            title = item.get('title', '')
                            if self._is_duplicate_title(title, seen_titles):
                                self.logger.info(f"Skipping duplicate document: {title}")
                                continue
                                
                            if 'v.' in title.lower():
                                self.logger.info(f"Skipping court document: {title} ({doc_type})")
                                continue
                                
                            url_with_key = f"{url}?api_key={self.api_key}"
                            full_text = self.get_document_text(url_with_key)

                            if len(full_text) < 5000:
                                continue
                            
                            self.logger.info(f"Retrieved document: {title} ({len(full_text)} characters) from {url_with_key}")

                            # Add title to seen titles after processing
                            seen_titles.append(title.lower().strip())
                            
                            results.append({
                                "title": title,
                                "text": full_text,
                                "url": url_with_key,
                                "keyword": topic
                            })
                    else:
                        self.logger.error(f"API request failed with status code: {response.status_code}")
                except Exception as e:
                    self.logger.error(f"Error processing GovInfo query for {topic}: {e}")
                
            # Create DataFrame and normalize to match expected format
            if results:
                self.logger.info(f"Retrieved {len(results)} government documents in total")
                self.articles_df = pd.DataFrame(results)
            else:
                self.logger.warning("No government documents found matching the search criteria")
                
        except Exception as e:
            self.logger.error(f"Error in Gov integration: {e}")


if __name__ == "__main__":
    keywords = ['tariffs']
    gov = Gov(keywords)  # Add Gov instance

    # Retrieve articles from all sources
    gov.get_articles()  # Get government articles

    final_df = gov.articles_df

    for index, row in final_df.iterrows():
        print(f"Title: {row['title']}")
        print(f"Text: {row['text'][1000:1050]}")
        print(f"URL: {row['url']}")
        print(f"Keyword: {row['keyword']}")
        print("--------------------")