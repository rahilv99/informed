## Given a user PDF, create DF with article data and find 2 additional articles that are most similar to the user PDF

from user_topics import UserTopics
import pandas as pd
import numpy as np
import PyPDF2
import requests
import os
from bs4 import BeautifulSoup
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

        self.user_topics = user_topics
    
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

        return primary.paperId

    def _paper_to_dict(self, paper):
        return {
            'paperId': paper.paperId,
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': [author.name for author in paper.authors],
            'arxiv': paper.externalIds['ArXiv'] if paper.externalIds and 'ArXiv' in paper.externalIds else None,
            'fieldsOfStudy': paper.fieldsOfStudy,  
            'influentialCitationCount': paper.influentialCitationCount,
            'openAccessPdf': paper.openAccessPdf,
            'publicationDate': paper.publicationDate,
            'publicationTypes': paper.publicationTypes, 
            'score': paper.referenceCount + paper.citationCount + paper.influentialCitationCount,
            'url': paper.url,
            # ... add more attributes as needed ...
        }
    
    def _flatten_paper(self, obj):
        flat_data = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_data[f"{key}_{sub_key}"] = sub_value
            elif isinstance(value, list) and value and isinstance(value[0], dict):  
                for i, item in enumerate(value):
                    for sub_key, sub_value in item.items():
                        flat_data[f"{key}_{i}_{sub_key}"] = sub_value
            else:
                flat_data[key] = value
        return flat_data
    
    def _extract_entities(self, input_text):
        doc = nlp(input_text)
        # Extracting named entities and common nouns
        entities = [ent.text for ent in doc.ents] + [token.text for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities) 

    def _user_relevance(self, df):
        if df.empty:
            return
        
        column_data = df['abstract'].tolist()
        extracted_entities = [self._extract_entities(text) for text in column_data]

        entity_embeddings = model.encode(extracted_entities, convert_to_tensor=True)
        # Calculate cosine similarities between entity embeddings and user input embeddings 
        cosine_similarities_main = util.cos_sim(self.user_topics.user_input_embeddings, entity_embeddings).flatten()
        cosine_similarities_expanded = util.cos_sim(self.user_topics.expanded_embeddings, entity_embeddings).flatten()

        # Prioritize main input over expanded input
        cosine_similarities = cosine_similarities_main.numpy() * 0.65 + cosine_similarities_expanded.numpy() * 0.35

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
            corpus = [self._flatten_paper(self._paper_to_dict(citation)) for citation in citations]
            df = pd.DataFrame(corpus)
            # drop no abstract
            df = df.dropna(subset=['abstract'])

        else:
            print(f'0 results found via citations, attempting to find similar papers')

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
                corpus = [self._flatten_paper(self._paper_to_dict(result)) for result in results]
                df = pd.DataFrame(corpus)
                # drop no abstract
                df = df.dropna(subset=['abstract'])

            else:
                print('0 results found with similarity search, using only single paper')

        df = self._user_relevance(df)
        return df
   
    # Function to extract text from a PDF
    def _extract_pdf_text(self, pdf_link, scrape = False):

        def __download_pdf(pdf_link, output_dir="/tmp/"):
        # Download the PDF
            pdf_response = requests.get(pdf_link, stream=True)
            if pdf_response.headers.get("Content-Type", "").lower() != "application/pdf":
                return 'na'
            
            # Save the PDF
            arxiv_ID = pdf_link.split("/")[-1]
            file_path = os.path.join(output_dir, f"{arxiv_ID}.pdf")
            __save_pdf(self, pdf_response, file_path)
            print(f"Downloaded: {file_path}")
            return file_path

        def __find_pdf_link(url):
        # Access the journal's article page (HTML)
            article_response = requests.get(url)

            if article_response.status_code != 200:
                print(f"Failed to access article page. Status code: {article_response.status_code}")
                return None

            # Parse and find the PDF link
            soup = BeautifulSoup(article_response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if 'pdf' in link['href'].lower():
                    if not pdf_link.startswith('http'):
                        id = url.split('/')[-1]
                        return 'https://www.semanticscholar.org/reader/' + id
                    return link['href']
            return None

        def __save_pdf(self, pdf_response, file_path):
            """Save PDF content to the specified file path."""
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                for chunk in pdf_response.iter_content(chunk_size=1024):
                    f.write(chunk)


        if scrape:
            pdf_link = __find_pdf_link(pdf_link)
            if pdf_link == None:
                raise Exception("Invalid URL.")
        
        file_path = __download_pdf(pdf_link)
        if file_path == 'na':
            raise Exception("Invalid PDF link.")
        text = ""
        try:
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise Exception(f"Error reading PDF {file_path}: {e}")
        # delete file from path
        os.remove(file_path)
        return text
    
        # Get PDF for each
    def get_text(self, df):
        arxiv_extension = 'https://arxiv.org/pdf/'
        reccomeded_papers = pd.DataFrame()
        for index, row in df.iterrows():
            arxiv = row['arxiv']
            if arxiv:
                url = arxiv_extension + arxiv
                try:
                    text = self._extract_pdf_text(url)

                    new_row = pd.DataFrame([{
                        'title': row['title'],
                        'abstract': row['abstract'],
                        'text': text,
                        'score': row['score'],
                        'authors': row['authors'],
                        'url': row['url'],
                        'source_type': 'semanticscholar'
                    }])
                    reccomeded_papers = pd.concat([reccomeded_papers, new_row], ignore_index=True)
                    if len(reccomeded_papers) == 2:
                        break
                except Exception as e:
                    print(f"Error extracting text using Arxiv: {e}")
            else:
                url = row['url']
                try:
                    text = self._extract_pdf_text(url, scrape = True)
                    
                    new_row = pd.DataFrame([{
                        'title': row['title'],
                        'abstract': row['abstract'],
                        'text': text,
                        'score': row['score'],
                        'authors': row['authors'],
                        'url': row['url'],
                        'source_type': 'semanticscholar'
                    }])
                    reccomeded_papers = pd.concat([reccomeded_papers, new_row], ignore_index=True)

                    if len(reccomeded_papers) == 2:
                        break
                except Exception as e:
                    print(f"Error extracting text using URL: {e}")
        return reccomeded_papers






user_topics = UserTopics()

pdf_path = 'data/attention_is_all_you_need.pdf'
pdf_title = 'Attention is All You Need'
dd = DeepDive(pdf_path, pdf_title, user_topics)
df = dd.find_relevant_papers()
recommended_papers = dd.get_text(df)

# save recommended papers to csv
recommended_papers.to_csv('data/recommended_papers.csv', index=False)