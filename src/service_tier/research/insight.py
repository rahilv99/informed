## Given a user PDF, create DF with article data and find 2 additional articles that are most similar to the user PDF

from user_topics import UserTopics
import pandas as pd
import numpy as np
import PyPDF2
import os
import time
import random
from semanticscholar import SemanticScholar

from sentence_transformers import SentenceTransformer, util
import spacy

model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")

# Retry mechanism parameters (exponential backoff)
max_retries = 10
base_delay = 0.5
max_delay = 15

class DeepDive:
    def __init__(self, pdf_path, pdf_title, user_topics):
        self.input_pdf = pdf_path
        self.input_title = pdf_title
        self.sch = SemanticScholar(timeout = 7, api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY'))

        self.user_input = user_topics.user_input
        self.user_embeddings = user_topics.user_embeddings
    
    def _find_paper(self):
        # Retry mechanism with exponential backoff
        for attempt in range(max_retries + 1):
            try:
                results = self.sch.search_paper(self.input_title)
                time.sleep(0.33) # API rate limit
            except Exception as e:
                print(f"Error searching for paper: {e}")
                if attempt == max_retries:
                    raise e

                delay = min(base_delay * 2 ** attempt, max_delay)
                jitter = random.uniform(0, 1)
                time.sleep(delay + jitter)
        
        primary = results[0]
        if self.input_title.lower() == primary.title.lower():
            print('result found for:', self.input_title)
        else:
            print('exact match not found, proceeding with closest match: ', primary.title)

        self.input_url = primary.url
        return primary.paperId

    def _extract_entities(self, input_text):
        doc = nlp(input_text)
        # Extracting named entities and common nouns
        entities = [ent.text for ent in doc.ents] + [token.text for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities) 

    def _user_relevance(self, df):
        if df.empty:
            return
        
        column_data = df['text'].tolist()
        extracted_entities = [self._extract_entities(text) for text in column_data]

        entity_embeddings = model.encode(extracted_entities, convert_to_tensor=True)
        # Calculate cosine similarities between entity embeddings and user input embeddings 
        cosine_similarities = util.cos_sim(self.user_embeddings, entity_embeddings).flatten().numpy()

        # normalize current score column
        scores = df['score'].tolist()
        citation_score = scores / np.max(scores)
        # Sort articles df using scores
        df['score'] = citation_score + cosine_similarities * 3
        df = df.sort_values(by='score', ascending=False)

        return df

    
    def find_relevant_papers(self):
        primary_paper_id = self._find_paper()
        print('looking for similar papers')
        for attempt in range(max_retries + 1):
            try:
                paper = self.sch.get_paper(primary_paper_id)
                time.sleep(0.33) # API rate limit
            except Exception as e:
                print(f"Error searching for paper: {e}")
                if attempt == max_retries:
                    raise e

                delay = min(base_delay * 2 ** attempt, max_delay)
                jitter = random.uniform(0, 1)
                time.sleep(delay + jitter)
        
        citations = paper.citations

        if len(citations) > 0:
            print(f'{len(citations)} results found')
            corpus = [{
                'title': citation.title, 
                'text': citation.abstract, 
                'url': citation.url,
                'score':  citation.referenceCount + citation.citationCount + citation.influentialCitationCount
            } for citation in citations]
            df = pd.DataFrame(corpus)
            # drop no abstract
            df = df.dropna(subset=['text'])

        else:
            print('0 results found via citations, attempting to find similar papers')

            for attempt in range(max_retries + 1):
                try:
                    results = self.sch.get_recommended_papers(primary_paper_id)
                    time.sleep(0.33) # API rate limit
                except Exception as e:
                    print(f"Error searching for paper: {e}")
                    if attempt == max_retries:
                        raise e
                    delay = min(base_delay * 2 ** attempt, max_delay)
                    jitter = random.uniform(0, 1)
                    time.sleep(delay + jitter)
            
            if len(results) > 0:
                print(f'{len(results)} results found')
                corpus = [{
                'title': citation.title, 
                'text': citation.abstract, 
                'url': citation.url,
                'score':  citation.referenceCount + citation.citationCount + citation.influentialCitationCount
                } for citation in citations]
                df = pd.DataFrame(corpus)
                # drop no abstract
                df = df.dropna(subset=['text'])

            else:
                print('0 results found with similarity search, using only single paper')

        df = self._user_relevance(df).head(2)
        print(f'2 most relevant papers found: {df["title"].tolist()}')
        try:
            text = ''
            with open(self.input_pdf, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise Exception(f"Error reading user PDF: {e}")
        rows = [{
            'title': self.input_title,
            'text': text,
            'url': self.input_url,
        }]
        user_df = pd.DataFrame(rows)
        
        df = df.drop(columns=['score'])
        df = pd.concat([user_df, df], ignore_index=True)
        
        return df




user_topics = UserTopics()

pdf_path = 'data/attention_is_all_you_need.pdf'
pdf_title = 'Attention is All You Need'
dd = DeepDive(pdf_path, pdf_title, user_topics)
recommended_papers = dd.find_relevant_papers()

# save recommended papers to csv
recommended_papers.to_csv('data/recommended_papers.csv', index=False)