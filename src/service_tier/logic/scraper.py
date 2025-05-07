"""
Simplified web scraping functionality to extract text from URLs.
"""
import logging
import re
import requests
from bs4 import BeautifulSoup

class Scraper:
    """
    Simplified web scraping class to extract text from URLs.
    """

    def __init__(self):
        self.logger = logging.getLogger('scraper')

    def fetch_url(self, url: str) -> str:
        """
        Fetch the content of a URL using requests.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {e}")
            return ""

    def extract_text(self, html_content: str) -> str:
        """
        Extract and clean text from HTML content using BeautifulSoup.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()

            # Get text content
            text = soup.get_text()

            # Clean up text: break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            self.logger.info(f"Extracted {len(text)} characters")
            self.logger.info(f"Extracted text: {text[:100]}...")  # Log first 100 characters for debugging

            return self.clean_text(text)
        except Exception as e:
            self.logger.error(f"Error extracting text from HTML: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by normalizing whitespace and fixing common issues.
        """
        if not text:
            return ""

        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)

        # Replace multiple newlines with a single newline
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Fix common issues like hyphenation
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)

        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

        return text.strip()

    def scrape(self, url: str) -> str:
        """
        Scrape text content from a given URL.
        """
        self.logger.info(f"Scraping URL: {url}")
        html_content = self.fetch_url(url)
        if not html_content:
            return "Failed to retrieve content"
        return self.extract_text(html_content)