from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd
import spacy
import datetime
import os
import time
import random
import logging
import requests
import io
from bs4 import BeautifulSoup
import PyPDF2

from logic.user_topics_output import UserTopicsOutput
import common.sqs
import common.s3


# Constants
DEFAULT_ARTICLE_AGE = 7
MODEL = SentenceTransformer('./saved_model/all-MiniLM-L6-v2')
MAX_RETRIES = 10
BASE_DELAY = 0.33
MAX_DELAY = 15

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pulse')

# Base ArticleResource class
class ArticleResource:
    def __init__(self, user_topics_output):
        self.articles_df = pd.DataFrame()
        self.today = datetime.date.today()
        self.time_constraint = self.today - datetime.timedelta(days=DEFAULT_ARTICLE_AGE)
        self.user_input = user_topics_output.user_input
        self.user_embeddings = user_topics_output.user_embeddings
        self.nlp = spacy.load("en_core_web_sm")

    def _extract_entities(self, input_text):
        if not isinstance(input_text, str):
            return ""

        input_text = input_text[:5000]
        doc = self.nlp(input_text)
        entities = [ent.text for ent in doc.ents] + [token.text for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities)

    def normalize_df(self):
        self.articles_df.rename(columns={
            'Article Text': 'text', 'Abstract': 'text', 'domain': 'journal',
            'Title': 'title', 'Authors': 'author'
        }, inplace=True)
        self.articles_df.drop_duplicates(subset=['title'], inplace=True)

    def rank_data(self, scoring_column='text'):
        if self.articles_df.empty:
            return

        # Fill NaN or None values in the scoring column with empty strings
        self.articles_df[scoring_column] = self.articles_df[scoring_column].fillna("")

        entities = self.articles_df[scoring_column].apply(self._extract_entities)
        entities_list = entities.tolist()  # Convert Series to list
        embeddings = MODEL.encode(entities_list, convert_to_tensor=True)
        
        self.articles_df['score'] = util.cos_sim(self.user_embeddings, embeddings).flatten().numpy() 
        self.articles_df.sort_values(by='score', ascending=False, inplace=True)
        self.articles_df = self.articles_df.head(5)

    @staticmethod
    def finalize_df(resources):
        combined_df = pd.concat([r.articles_df for r in resources])
        combined_df.drop_duplicates(subset=['title'], inplace=True)
        return combined_df.sort_values(by='score', ascending=False).head(5)

    def fetch_with_retry(self, func, *args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                time.sleep(min(BASE_DELAY * 2 ** attempt + random.uniform(0, 1), MAX_DELAY))
'''
# PubMed Integration
class PubMed(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.logger = logging.getLogger('pulse.pubmed')

    def get_articles(self):
        try:
            self.logger.info(f"Searching for PubMed articles related to: {self.user_input}")
            Entrez.email = 'rahil.verma@duke.com'
            topics = self.user_input
            query = f'{topics[0]} AND "{self.time_constraint}"[Date] : "{self.today}"[Date]'
            for t in topics[1:]:
                query += f' OR {t} AND "{self.time_constraint}"[Date] : "{self.today}"[Date]'
            try:
                handle = self.fetch_with_retry(Entrez.esearch, db='pubmed', term=query, sort='relevance', retmax='500', retmode='xml')
                results = Entrez.read(handle)
                id_list = results['IdList']
            except Exception as e:
                self.logger.error(f"Error fetching PubMed query: {e}")

            try:
                handle = self.fetch_with_retry(Entrez.efetch, db='pubmed', id=','.join(id_list), retmode='xml')
                papers = Entrez.read(handle)
                rows = []
                for article in papers['PubmedArticle']:
                    data = {
                        'title': article['MedlineCitation']['Article'].get('ArticleTitle', 'N/A'),
                        'text': ' '.join(article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', '')),
                        'url': f"https://www.ncbi.nlm.nih.gov/pubmed/{article['MedlineCitation']['PMID']}"
                    }
                    rows.append(data)
                self.articles_df = pd.DataFrame(rows)
                self.normalize_df()
            except Exception as e:
                self.logger.error(f"Error fetching PubMed articles: {e}")
        except Exception as e:
            self.logger.error(f"Error in PubMed integration: {e}")


# Semantic Scholar Integration
class Sem(ArticleResource):
    def __init__(self, user_topics_output):
        super().__init__(user_topics_output)
        self.sch = SemanticScholar(timeout = 7, api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY'))
        self.logger = logging.getLogger('pulse.sem')

    def get_articles(self):
        self.logger.info(f"Searching for Semantic Scholar articles related to: {self.user_input}")
        try:
            results = []
            for k in self.user_input:
                try:
                    response = self.fetch_with_retry(self.sch.search_paper, query=k, publication_date_or_year=f'{self.time_constraint.strftime("%Y-%m-%d")}:{self.today.strftime("%Y-%m-%d")}')
                    results += response.items
                except Exception as e:
                    self.logger.error(f"Error fetching Semantic Scholar query for {k}: {e}")

            rows = [{'title': r.title, 'text': r.abstract, 'url': r.url} for r in results]
            self.articles_df = pd.DataFrame(rows)
            self.normalize_df()
        except Exception as e:
            self.logger.error(f"Error in Semantic Scholar integration: {e}")
'''
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

# Main Execution
def handler(payload):
    user_id = payload.get("user_id")
    user_name = payload.get("user_name")
    user_email = payload.get("user_email")
    plan = payload.get("plan")
    episode = payload.get("episode")

    user_topics_output = UserTopicsOutput(episode, user_id)

    gov = Gov(user_topics_output)

    gov.get_articles()

    gov.rank_data()

    final_df = ArticleResource.finalize_df([gov])

    print(final_df)
    #final_df.to_csv('./data/final_df.csv', index=False)

    common.s3.save_serialized(user_id, episode, "PULSE", {
            "final_df": final_df,
    })

    # Send message to SQS
    try:
        next_event = {
            "action": "e_nlp",
            "payload": { 
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "plan": plan,
            "episode": episode,
            "ep_type": "pulse"
            }
        }
        common.sqs.send_to_sqs(next_event)
        print(f"Sent message to SQS for next action {next_event['action']}")
    except Exception as e:
        print(f"Exception when sending message to SQS {e}")

if __name__ == "__main__":
    handler(None)