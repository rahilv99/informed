from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd
import spacy
#import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
#import seaborn as sns
from tqdm import tqdm
import pickle
# GDELT data
from gdeltdoc import GdeltDoc, Filters, near
import datetime
#PubMed Data
from Bio import Entrez
# Semantic Scholar
from semanticscholar import SemanticScholar
# arxiv stuff
import arxiv
import datetime
import pandas as pd
import numpy as np
import PyPDF2
import os
import pickle
import time
import random

from research.user_topics import UserTopics

DEFAULT_ARTICLE_AGE = 7     # one week ago

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and effective model
pd.set_option('display.max_colwidth', 15)

# Retry mechanism parameters (exponential backoff)
max_retries = 10
base_delay = 0.5
max_delay = 15

class ArticleResource:
    def __init__(self, user_topics):
        # Standardizing month mapping
        self.articles_df = pd.DataFrame()
        self.month_mapping = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
            'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
            'No Data': np.nan
        }
        self.today = datetime.date.today()
        self.time_constraint = self.today - datetime.timedelta(days=DEFAULT_ARTICLE_AGE)
        self.user_topics = user_topics
        self.nlp = spacy.load("en_core_web_sm")# Load spaCy model for keyword extraction

    def _extract_entities(self, input_text):
        doc = self.nlp(input_text)
        # Extracting named entities and common nouns
        entities = [ent.text for ent in doc.ents] + [token.text for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities) 
    
    def normalize_df(self):
        rename_map = {
            'Article Text': 'text',
            'Abstract': 'text',
            'domain': 'journal',
            'Title': 'title',
            'Authors': 'author'
        }
        self.articles_df.rename(columns=rename_map, inplace=True)
        self.articles_df = self.articles_df.drop_duplicates(subset=['title'])  # Remove duplicates based on title
    
    def rank_data(self, scoring_column='text', threshold=0.3, penalty = 0, intermeadiate = False):
        if self.articles_df.empty:
            return
        
        column_data = self.articles_df[scoring_column].tolist()
        extracted_entities = [self._extract_entities(text) for text in column_data]
        self.articles_df['entities'] = extracted_entities

        entity_embeddings = model.encode(extracted_entities, convert_to_tensor=True)
        # Calculate cosine similarities between entity embeddings and user input embeddings 
        cosine_similarities_main = util.cos_sim(self.user_topics.user_input_embeddings, entity_embeddings).flatten()
        cosine_similarities_expanded = util.cos_sim(self.user_topics.expanded_embeddings, entity_embeddings).flatten()

        # Prioritize main input over expanded input
        cosine_similarities = cosine_similarities_main.numpy() * 0.65 + cosine_similarities_expanded.numpy() * 0.35

        # Sort articles df using scores
        self.articles_df['score'] = cosine_similarities - penalty
        self.articles_df = self.articles_df.sort_values(by='score', ascending=False)

        if intermeadiate:
            self.articles_df = self.articles_df[self.articles_df['score'] > threshold]
            self.articles_df = self.articles_df.head(20)
            self.articles_df = self.articles_df.drop(columns=['score'])
            print(f'size of df after title filtering {len(self.articles_df)}')
        else:
            self.articles_df = self.articles_df.head(5)            
                
        # display score, title, and extracted entity
        # for rank, (score, title, entity) in enumerate(zip(self.articles_df['score'], self.articles_df[scoring_column], self.articles_df['entities']), start=1):
        #     print(f'Rank {rank}: Score = {score:.4f} Scoring_Column: {title} Entitites: {entity}')

    @staticmethod
    def finalize_df(resc_array):
        df_array = [r.articles_df for r in resc_array]
        columns_to_keep = ['title', 'text', 'journal', 'score', 'author', 'source_type', 'url']

        filtered_dfs = [df.head(5)[columns_to_keep] for df in df_array]
        
        # Concatenate filtered DataFrames into one
        result = pd.concat(filtered_dfs, ignore_index=True, sort=False)

        # drop repeated titles
        result = result.drop_duplicates(subset=['title'])

        # sort and return the top 5
        result = result.sort_values(by='score', ascending=False)
        result = result.head(5)
        return result


class GDelt(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)
        self.gd = GdeltDoc()

    def _normalize_df(self):
        # Ensure 'seendate' is in datetime format
        self.articles_df['seendate'] = pd.to_datetime(self.articles_df['seendate'])

        # Filter rows and extract date components
        self.articles_df = self.articles_df[self.articles_df['language'] == 'English']
        self.articles_df['Publication Day'] = self.articles_df['seendate'].dt.day
        self.articles_df['Publication Month'] = self.articles_df['seendate'].dt.month
        self.articles_df['Publication Year'] = self.articles_df['seendate'].dt.year
        # drop url_mobile
        self.articles_df = self.articles_df.drop(columns=['url_mobile'])

        # sort descending
        self.articles_df = self.articles_df.sort_values(by=['Publication Year','Publication Month','Publication Day'], ascending=[False,False,False])
        self.articles_df['source_type'] = 'gdelt'
        self.articles_df['author'] = 'None'
        super().normalize_df()

    def _scrape_article_text(self, url):
        try:
            # Send a GET request to the webpage
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 422:
                print('MFA required')
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the main text (customize based on the website structure)
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs if p.get_text()])
            return article_text
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def get_articles(self):
        for k in self.user_topics.all_input:
            f = Filters(
                start_date = self.time_constraint.strftime('%Y-%m-%d'),
                end_date = self.today.strftime('%Y-%m-%d'),
                num_records = 100,
                keyword = k,
                country = ['US','UK','CA','AU','CH']
            )
            for k in self.user_topics.all_input:
                for attempt in range(max_retries + 1):
                    try:
                        results = self.gd.article_search(f)
                    except Exception as e:
                        print(f"Error searching for paper: {e}")
                        if attempt == max_retries:
                            raise e
                        delay = min(base_delay * 2 ** attempt, max_delay)
                        jitter = random.uniform(0, 1)
                        time.sleep(delay + jitter)
            
            self.articles_df = pd.concat([self.articles_df, results])

        self._normalize_df()
        print(f'**** GDELT Preview ****')
        print(self.articles_df.head())

    def get_articles_content(self):
        if self.articles_df.empty:
            self.articles_df['score'] = None
            self.articles_df['text'] = None
            return
        
        self.articles_df['text'] = self.articles_df['url'].apply(self._scrape_article_text)
        # keep articles with text over 1000 characters
        self.articles_df = self.articles_df.dropna(subset=['text'])
        self.articles_df = self.articles_df[self.articles_df['text'].str.len() > 1000]

        # shorten articles more than 30000 characters
        self.articles_df['text'] = self.articles_df['text'].apply(lambda x: x[:30000] if len(x) > 30000 else x)
    

class PubMed(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)

    #Using e-search API to find PubMed search results
    def _search(self, query):
        Entrez.email = 'rahil.verma@duke.com'
        handle = Entrez.esearch(db='pubmed',
                                sort='relevance',
                                retmax='50',
                                retmode='xml',
                                term=query)
        results = Entrez.read(handle)
        return results
    
    def _fetch_details(self, id_list):
        ids = ','.join(id_list)
        Entrez.email = 'email@example.com'
        handle = Entrez.efetch(db='pubmed',
            retmode='xml',
            id=ids)
        results = Entrez.read(handle)
        return results
    
    def _parse_pub_date(self, pub_date):
        """ Extracts and formats the publication date from the PubDate field. """
        if 'Year' in pub_date:
            year = pub_date.get('Year', 'No Data')
            month = pub_date.get('Month', 'No Data')
            day = pub_date.get('Day', 'No Data')
            return year,month,day
        return 'No Data', 'No Data', 'No Data'
    
    def _normalize_df(self):
        self.articles_df = (
            self.articles_df[self.articles_df['language'] == 'eng']  # Filter rows where language is 'eng'
            .drop_duplicates(subset='PMID')  # Remove duplicates based on PMID
            .replace({'Publication Month': self.month_mapping,  # Standardize months
                    'Publication Year': {'No Data': np.nan},  # Handle missing years
                    'Publication Day': {'No Data': np.nan}})  # Handle missing days
        )
        # Convert year and day to numeric and sort
        self.articles_df['Publication Year'] = pd.to_numeric(self.articles_df['Publication Year'], errors='coerce')
        self.articles_df['Publication Day'] = pd.to_numeric(self.articles_df['Publication Day'], errors='coerce')
        # Sort by year, month, and day (descending order)
        self.articles_df.sort_values(by=['Publication Year', 'Publication Month', 'Publication Day'], 
                   ascending=[False, False, False], 
                   inplace=True)
        self.articles_df['source_type'] = 'pubmed'
        super().normalize_df()

    def get_articles(self):
        id_list = []
        # search query with each keyword and date bounds
        for k in self.user_topics.all_input:
            query = f'{k} AND ("{self.time_constraint.strftime("%Y/%m/%d")}"[Date - Publication] : "{self.today.strftime("%Y/%m/%d")}"[Date - Publication])'

            # Retry mechanism with exponential backoff
            for attempt in range(max_retries + 1):
                try:
                    ret = self._search(query)
                    time.sleep(0.33) # API rate limit
                except Exception as e:
                    print(f"Error searching for paper: {e}")
                    if attempt == max_retries:
                        raise e

                    delay = min(base_delay * 2 ** attempt, max_delay)
                    jitter = random.uniform(0, 1)
                    time.sleep(delay + jitter)
            
            for id in ret['IdList']:
                id_list.append(id)

        papers = self._fetch_details(id_list)
        for i, record in enumerate (papers['PubmedArticle']):
            pmid = record['MedlineCitation']['PMID']
            article = record['MedlineCitation']['Article']  # Extract the article details from the 'MedlineCitation' section
            title = article.get('ArticleTitle', 'Title Not Available')  # Safely fetch the title of the article
            abstract = ' '.join(article['Abstract']['AbstractText']) if 'Abstract' in article else ''  # Join the text elements of the abstract into a single string, if available
            authors_list = ', '.join(a.get('ForeName', '') + ' ' + a.get('LastName', '') for a in article.get('AuthorList', [])) or 'Authors Not Available'  # Compile a list of author names, formatted as 'First Name Last Name'
            journal = article['Journal'].get('Title', 'Journal Not Available')  # Get the title of the journal where the article was published
            keys = ', '.join(k['DescriptorName'] for k in record['MedlineCitation'].get('MeshHeadingList', [])) or 'Keywords Not Available'  # Extract keywords from the 'MeshHeadingList', if available
            pub_year,pub_month,pub_day = self._parse_pub_date(article['Journal']['JournalIssue']['PubDate'])  # Parse the publication date using a helper function
            lang = article.get('Language', 'Language Not Available')  # Get the language of the article, if available
            lang = lang[0]
            url = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"  # Construct the URL to the PubMed page for this article

            for id_item in article.get("ELocationID"):
                if id_item.attributes["EIdType"] == "doi":
                    publisher_url = f"https://doi.org/{id_item}"
                    break
                else:
                    publisher_url = 'None'

            # Prepare the data row
            new_row = pd.DataFrame({
                'PMID': [pmid],
                'Title': [title],
                'Abstract': [abstract],
                'Authors': [authors_list],
                'journal': [journal],
                'Keywords': [keys],
                'url': [url],
                'Publication Year': [pub_year],
                'Publication Month': [pub_month],
                'Publication Day': [pub_day],
                'language': [lang],
                'Publisher URL': [publisher_url]
            })

            self.articles_df = pd.concat([self.articles_df, new_row], ignore_index=True)  # Add the extracted data to the DataFrame
        
        self._normalize_df()
        print(f'**** Pubmed Preview ****')
        print(self.articles_df.head())
        
class Arxiv(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)
        self.client = arxiv.Client()

    def _parse_pub_date_arxiv(self, pub_date):
        """ Extracts and formats the publication date from the arxiv field. """
        year = getattr(pub_date, 'year', "No Data")
        month = getattr(pub_date, 'month', "No Data")
        day = getattr(pub_date, 'day', "No Data")
        return year, month, day

        
    def _normalize_df(self):
        self.articles_df = (
            self.articles_df.drop_duplicates(subset='arxiv_ID')
            .replace({'Publication Month': self.month_mapping,  # Standardize months
                    'Publication Year': {'No Data': np.nan},  # Handle missing years
                    'Publication Day': {'No Data': np.nan}})  # Handle missing days
        )
        # Convert year and day to numeric and sort
        self.articles_df['Publication Year'] = pd.to_numeric(self.articles_df['Publication Year'], errors='coerce')
        self.articles_df['Publication Day'] = pd.to_numeric(self.articles_df['Publication Day'], errors='coerce')
        # Sort by year, month, and day (descending order)
        self.articles_df.sort_values(by=['Publication Year', 'Publication Month', 'Publication Day'], 
                   ascending=[False, False, False], 
                   inplace=True)
        self.articles_df['source_type'] = 'arxiv'
        super().normalize_df()

    # Function to download PDF
    def _download_pdf(self, url, arxiv_ID, output_dir="/tmp/arxiv"):

        def __find_pdf_link(soup):
            """Find the first PDF link in the HTML."""
            for link in soup.find_all('a', href=True):
                if 'pdf' in link['href'].lower():
                    return link['href']
            return None
        
        def __save_pdf(pdf_response, file_path):
            """Save PDF content to the specified file path."""
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                for chunk in pdf_response.iter_content(chunk_size=1024):
                    f.write(chunk)
        
        # Access the journal's article page (HTML)
        article_response = requests.get(url)

        if article_response.status_code != 200:
            print(f"Failed to access article page for arXiv ID {arxiv_ID}. Status code: {article_response.status_code}")
            return 'na'

        # Parse and find the PDF link
        soup = BeautifulSoup(article_response.text, 'html.parser')
        pdf_link = __find_pdf_link(soup)
        if not pdf_link:
            print(f"No PDF link found on the article page for arXiv ID {arxiv_ID}.")
            return 'na'
        
        # Build the full PDF URL if relative
        if not pdf_link.startswith('http'):
            pdf_link = 'https://arxiv.org/' + pdf_link

        # Download the PDF
        pdf_response = requests.get(pdf_link, stream=True)
        if pdf_response.headers.get("Content-Type", "").lower() != "application/pdf":
            print(f"Failed to retrieve PDF for arXiv ID {arxiv_ID}. Invalid PDF link.")
            return 'na'
        
        # Save the PDF
        file_path = os.path.join(output_dir, f"{arxiv_ID}.pdf")
        __save_pdf(pdf_response, file_path)
        print(f"Downloaded: {file_path}")
        return file_path

    # Function to extract text from a PDF
    def _extract_pdf_text(self, file_path):
        text = ""
        try:
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text

    def get_articles(self):
        preprints = []

        for k in self.user_topics.all_input:
            # TODO see if recent criteria can be provided to Search rather than getting all docs and then filtering them out
            search = arxiv.Search(
                query = k,
                max_results = 50,      # TODO - this was 200 originally and changed it
                sort_by = arxiv.SortCriterion.SubmittedDate,
                sort_order = arxiv.SortOrder.Descending)

            # Retry mechanism with exponential backoff
            for attempt in range(max_retries + 1):
                try:
                    results = self.client.results(search)
                    time.sleep(0.33) # API rate limit
                except Exception as e:
                    print(f"Error searching for paper: {e}")
                    if attempt == max_retries:
                        raise e
                    delay = min(base_delay * 2 ** attempt, max_delay)
                    jitter = random.uniform(0, 1)
                    time.sleep(delay + jitter)

            
            all_results = list(results)
            for result in all_results:
                if result.published.date() >= self.time_constraint:
                    preprints.append(result)

        if (len(preprints) == 0):
            print(f'Arixv has no recent articles')
            self.articles_df = pd.DataFrame(columns=['Publication Year', 'Publication Month', 'Publication Day', 'Abstract', 'Authors', 'journal', 'url', 'Title', 'arxiv_ID'])
        else:
            data = []
            for paper in preprints:
                year,month,day = self._parse_pub_date_arxiv(paper.published.date())
                entry = {
                    'Publication Year': year,
                    'Publication Month': month,
                    'Publication Day': day,
                    'Abstract': paper.summary if paper.summary else "No Data",
                    'Authors': [author.name for author in paper.authors] if paper.authors else "No Data",
                    'journal': paper.journal_ref if paper.journal_ref else "No Data",
                    'url': paper.entry_id if paper.entry_id else "No Data",
                    'Title': paper.title if paper.title else "No Data",
                    'arxiv_ID': paper.get_short_id() if paper.get_short_id() else "No Data"
                }
                data.append(entry)
            self.articles_df = pd.DataFrame(data)

        self._normalize_df()
        print(f'**** Arixiv Preview ****')
        print(self.articles_df.head())
    
    def get_articles_content(self):
        if self.articles_df.empty:
            self.articles_df['score'] = None
            self.articles_df['text'] = None
            return
        
        for i, row in enumerate(self.articles_df.itertuples()):
            arxiv_ID = row.arxiv_ID
            url = row.url
            print(f"Downloading number {i+1} of {len(self.articles_df)}: {arxiv_ID}")
            try:
                path = self._download_pdf(url, arxiv_ID)
                # update table with pdf location
                if path != 'na':
                    print('Extracting text from PDF')
                    self.articles_df.loc[self.articles_df['arxiv_ID'] == arxiv_ID, 'text'] = self._extract_pdf_text(path)
            except Exception as e:
                print(f"Error downloading {arxiv_ID}: {e}")

class Sem(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)
        self.sch = SemanticScholar(timeout = 7)
        self.api_key = 'ZIiAm4GlS429RZe7AUTwDaK2jHCKo6Lh60W1BimJ'
        
    def _normalize_df(self):
        self.articles_df = self.articles_df.drop_duplicates(subset='id')
        # Convert year and day to numeric and sort
        self.articles_df['Publication Year'] = pd.to_numeric(self.articles_df['Publication Year'], errors='coerce')
        self.articles_df['source_type'] = 'semanticscholar'
        super().normalize_df()

    # can add function to download PDF if openAccess is True

    def paper_to_dict(self, paper):
        """
        Convert a Paper object to a dictionary suitable for creating a DataFrame row.
        """
        paper_dict = {
            "id": paper.paperId,
            "Title": paper.title,
            "Abstract": paper.abstract,
            "journal": paper.venue,
            "Publication Year": paper.year,
            "url": paper.url,
            "openAccessPdf_url": paper.openAccessPdf['url'] if paper.openAccessPdf else None,
            "fieldsOfStudy": [field["category"] for field in paper.s2FieldsOfStudy],
            "Authors": ', '.join([author["name"] for author in paper.authors]),
            #"externalIds": paper.externalIds,
        }
        return paper_dict

    # Convert a list of Paper objects to a DataFrame
    def papers_to_dataframe(self, papers):
        """
        Convert a list of Paper objects into a pandas DataFrame.
        """
        rows = [self.paper_to_dict(paper) for paper in papers]
        return pd.DataFrame(rows)

    def get_articles(self):
        self.articles_df = pd.DataFrame()

        today_str = self.today.strftime('%Y-%m-%d')
        time_str = self.time_constraint.strftime('%Y-%m-%d')
        date_range = f"{time_str}:{today_str}"

        for k in self.user_topics.all_input:

            # Retry mechanism with exponential backoff
            for attempt in range(max_retries + 1):
                try:
                    results = self.sch.search_paper(k, publication_date_or_year=date_range, api_key=self.api_key)
                    time.sleep(1) # API rate limit
                except Exception as e:
                    print(f"Error searching for paper: {e}")
                    if attempt == max_retries:
                        raise e

                    delay = min(base_delay * 2 ** attempt, max_delay)
                    jitter = random.uniform(0, 1)
                    time.sleep(delay + jitter)
        

            df = self.papers_to_dataframe(results.items)
            self.articles_df = pd.concat([self.articles_df, df])
        
        # drop empty abstract rows
        self.articles_df = self.articles_df.dropna(subset=['Abstract'])
        

        if (len(self.articles_df) == 0):
            print(f'Semantic scholar has no recent articles')
            self.articles_df = pd.DataFrame(columns=['Publication Year', 'Abstract', 'Authors', 'journal', 'url', 'Title', 'openAccessPdf_url', 'fieldsOfStudy', 'isOpenAccess', 'id'])
        
        self._normalize_df()
        print(f'**** Semantic Scholar Preview ****')
        print(self.articles_df.head())
        

user_topics = UserTopics()

#gdelt = GDelt(user_topics)
pubmed = PubMed(user_topics)
arv = Arxiv(user_topics)
sem = Sem(user_topics)

#gdelt.get_articles()
pubmed.get_articles()
arv.get_articles()
sem.get_articles()

# this part is for abstract ranking first, then retrieve pdf... not exactly necessary for our use case
#arv.rank_data(intermeadiate = True)
#gdelt.rank_data('title', intermeadiate = True)

#gdelt.get_articles_content()
#arv.get_articles_content()

pubmed.rank_data()
#gdelt.rank_data()
arv.rank_data() # These two COULD  have pdfs, we don't get rn
sem.rank_data()

final_df = ArticleResource.finalize_df([pubmed, sem, arv])
print(f'Final DF: {final_df}')

# save a csv 
final_df.to_csv('./data/final_df.csv', index=False)
