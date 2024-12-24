from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd
import spacy
import datetime
from Bio import Entrez
from semanticscholar import SemanticScholar
import arxiv
import os
import time
import random

from user_topics import UserTopics

# Constants
DEFAULT_ARTICLE_AGE = 7
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
MAX_RETRIES = 10
BASE_DELAY = 0.5
MAX_DELAY = 15

# Base ArticleResource class
class ArticleResource:
    def __init__(self, user_topics):
        self.articles_df = pd.DataFrame()
        self.today = datetime.date.today()
        self.time_constraint = self.today - datetime.timedelta(days=DEFAULT_ARTICLE_AGE)
        self.user_topics = user_topics
        self.nlp = spacy.load("en_core_web_sm")

    def _extract_entities(self, input_text):
        if not isinstance(input_text, str):
            return ""
        doc = self.nlp(input_text)
        entities = [ent.text for ent in doc.ents] + [token.text for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities)

    def normalize_df(self):
        self.articles_df.rename(columns={
            'Article Text': 'text', 'Abstract': 'text', 'domain': 'journal',
            'Title': 'title', 'Authors': 'author'
        }, inplace=True)
        self.articles_df.drop_duplicates(subset=['title'], inplace=True)

    def rank_data(self, scoring_column='text', threshold=0.3, penalty=0):
        if self.articles_df.empty:
            return

        print(f"Preview before ranking: {self.articles_df.head()}")

        # Fill NaN or None values in the scoring column with empty strings
        self.articles_df[scoring_column] = self.articles_df[scoring_column].fillna("")

        self.articles_df['entities'] = self.articles_df[scoring_column].apply(self._extract_entities)
        entities_list = self.articles_df['entities'].tolist()  # Convert Series to list
        embeddings = MODEL.encode(entities_list, convert_to_tensor=True)
        main_sim = util.cos_sim(self.user_topics.user_input_embeddings, embeddings).flatten().numpy()
        exp_sim = util.cos_sim(self.user_topics.expanded_embeddings, embeddings).flatten().numpy()
        
        self.articles_df['score'] = main_sim * 0.65 + exp_sim * 0.35 - penalty
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

# PubMed Integration
class PubMed(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)

    def get_articles(self):
        try:
            Entrez.email = 'rahil.verma@duke.com'
            id_list = []
            for k in self.user_topics.all_input:
                try:
                    query = f'{k} AND "{self.time_constraint}"[Date] : "{self.today}"[Date]'
                    handle = self.fetch_with_retry(Entrez.esearch, db='pubmed', term=query, sort='relevance', retmax='50', retmode='xml')
                    results = Entrez.read(handle)
                    id_list.extend(results['IdList'])
                except Exception as e:
                    print(f"Error fetching PubMed query for {k}: {e}")

            try:
                handle = self.fetch_with_retry(Entrez.efetch, db='pubmed', id=','.join(id_list), retmode='xml')
                papers = Entrez.read(handle)
                rows = []
                for article in papers['PubmedArticle']:
                    data = {
                        'title': article['MedlineCitation']['Article'].get('ArticleTitle', 'N/A'),
                        'text': ' '.join(article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', '')),
                        'journal': article['MedlineCitation']['Article']['Journal']['Title'],
                        'author': ', '.join(a.get('LastName', '') for a in article['MedlineCitation']['Article'].get('AuthorList', [])),
                        'url': f"https://www.ncbi.nlm.nih.gov/pubmed/{article['MedlineCitation']['PMID']}"
                    }
                    rows.append(data)
                self.articles_df = pd.DataFrame(rows)
                self.normalize_df()
            except Exception as e:
                print(f"Error fetching PubMed articles: {e}")
        except Exception as e:
            print(f"Error in PubMed integration: {e}")

# ArXiv Integration
class Arxiv(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)
        self.client = arxiv.Client()

    def get_articles(self):
        try:
            results = []
            for k in self.user_topics.all_input:
                try:
                    search = arxiv.Search(query=k, max_results=50, sort_by=arxiv.SortCriterion.SubmittedDate)
                    fetched_results = self.fetch_with_retry(self.client.results, search=search)
                    results += list(fetched_results)
                except Exception as e:
                    print(f"General error fetching ArXiv query for {k}: {e}")

            if not results:
                print("No valid results fetched from Arxiv.")
                return

            rows = [{
                'title': r.title, 'text': r.summary, 'journal': r.journal_ref,
                'author': ', '.join(a.name for a in r.authors), 'url': r.entry_id
            } for r in results]
            self.articles_df = pd.DataFrame(rows)
            self.normalize_df()
        except Exception as e:
            print(f"Error in ArXiv integration: {e}")

# Semantic Scholar Integration
class Sem(ArticleResource):
    def __init__(self, user_topics):
        super().__init__(user_topics)
        self.sch = SemanticScholar(timeout = 7, api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY'))

    def get_articles(self):
        try:
            results = []
            for k in self.user_topics.all_input:
                try:
                    response = self.fetch_with_retry(self.sch.search_paper, query=k)
                    results += response.items
                except Exception as e:
                    print(f"Error fetching Semantic Scholar query for {k}: {e}")

            rows = [{
                'title': r.title, 'text': r.abstract, 'journal': r.venue,
                'author': ', '.join(a['name'] for a in r.authors), 'url': r.url
            } for r in results]
            self.articles_df = pd.DataFrame(rows)
            self.normalize_df()
        except Exception as e:
            print(f"Error in Semantic Scholar integration: {e}")

# Main Execution
def handler(event, context):
    user_topics = UserTopics()
    pubmed = PubMed(user_topics)
    arxiv_res = Arxiv(user_topics)
    sem = Sem(user_topics)

    pubmed.get_articles()
    arxiv_res.get_articles()
    sem.get_articles()

    pubmed.rank_data()
    arxiv_res.rank_data()
    sem.rank_data()

    final_df = ArticleResource.finalize_df([pubmed, arxiv_res, sem])
    final_df.to_csv('./data/final_df.csv', index=False)
    print(final_df)

if __name__ == "__main__":
    handler(None, None)