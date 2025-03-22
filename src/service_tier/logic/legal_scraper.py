from pulse import ArticleResource
import requests
import logging
import os
import io
from bs4 import BeautifulSoup
import PyPDF2
import pandas as pd

# Government Documents Integration

class Gov(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        # In production, this should be moved to environment variables
        self.api_key = os.environ.get('GOVINFO_API_KEY', "TqAJxayfmxCsJTFehykSs4agaZzrVFd7N0UJWBMc")
        self.search_url = f"https://api.govinfo.gov/search?api_key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}
        self.logger = logging.getLogger('pulse.gov')

    def get_articles(self):
        try:
            results = []
            for topic in self.user_input:
                # Create payload for API request with date range for last week
                payload = {
                    "query": f"{topic} publishdate:range({self.time_constraint.strftime('%Y-%m-%d')},{self.today.strftime('%Y-%m-%d')})",
                    "pageSize": 10,
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
                            
                            # Prioritize text content over PDF for easier processing
                            if 'txtLink' in links:
                                url = links['txtLink']
                                doc_type = 'txt'
                            elif 'pdfLink' in links:
                                url = links['pdfLink']
                                doc_type = 'pdf'
                            elif 'modsLink' in links:
                                url = links['modsLink']
                                doc_type = 'mods'
                            else:
                                continue
                                
                            # Get full text content for better relevance scoring
                            self.logger.info(f"Retrieving document: {item.get('title', '')} ({doc_type})")
                            full_text = self.get_document_text(url)

                            if len(full_text) < 1000:
                                continue
                            
                            results.append({
                                "title": item.get("title", ""),
                                "text": full_text,
                                "url": url
                            })
                    else:
                        self.logger.error(f"API request failed with status code: {response.status_code}")
                except Exception as e:
                    self.logger.error(f"Error processing GovInfo query for {topic}: {e}")
                
            # Create DataFrame and normalize to match expected format
            if results:
                self.logger.info(f"Retrieved {len(results)} government documents in total")
                self.articles_df = pd.DataFrame(results)
                self.normalize_df()
            else:
                self.logger.warning("No government documents found matching the search criteria")
                
        except Exception as e:
            self.logger.error(f"Error in Gov integration: {e}")
            
    def get_document_text(self, url):
        try:
            url_with_key = f"{url}?api_key={self.api_key}"
            response = self.fetch_with_retry(requests.get, url_with_key)
            
            if response.status_code == 200:
                # For HTML content
                if url.endswith('htm') or url.endswith('html'):
                    return self._extract_text_from_html(response.text)
                # For PDF content
                elif url.endswith('pdf'):
                    return self._extract_text_from_pdf(response.content)
                else:
                    return response.text
            else:
                self.logger.error(f"Failed to retrieve document: {response.status_code}")
                return f"Failed to retrieve document: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Error retrieving document: {e}")
            return f"Error retrieving document: {e}"
    
    def _extract_text_from_html(self, html_content):
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            
            # Get text content
            text = soup.get_text()

            # Get links
            links = soup.find_all('a')

            for link in links:
                link = link.get('href')
                if 'pdf' in link:
                    self.logger.info(f"Following link: {link}")
                    try:
                        response = requests.get(link)
                        if response.status_code == 200:
                            text += f"\n{self._extract_text_from_pdf(response.content)}"
                        else:
                            self.logger.error(f"Failed to retrieve linked document: {response.status_code}")
                    except Exception as e:
                        self.logger.error(f"Error retrieving linked document: {e}")

            
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
    
    def _extract_text_from_pdf(self, pdf_content):
        try:
            self.logger.info("Attempting to extract text using PyPDF2")
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                self.logger.warning("PDF is encrypted, cannot extract text")
                return "PDF is encrypted, cannot extract text"
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            self.logger.info(f"Successfully extracted text from PDF using PyPDF2 ({len(text)} characters)")
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            return "Error extracting text from PDF"