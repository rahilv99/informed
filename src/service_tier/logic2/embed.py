"""
Article clustering functionality using sentence transformers and document-based
clustering
"""

import numpy as np
import pandas as pd
import logging
import spacy
import psycopg2
import boto3
import os
import pickle
import json
import voyageai

db_access_url = os.environ.get('DB_ACCESS_URL')

class ArticleClusterer:
    """Class for clustering news articles based on government documents"""
    def __init__(self, similarity_threshold=0.35, merge_threshold=0.80):
        self.logger = logging.getLogger('pulse.clustering')
        self.model = voyageai.Client()
        self.nlp = spacy.load("en_core_web_sm")
        self.similarity_threshold = similarity_threshold
        self.merge_threshold = merge_threshold
    
    def extract_entities(self, input_text):
        """Extract entities and nouns from text"""
        if not isinstance(input_text, str):
            return ""
        
        input_text = input_text[1000:]
        doc = self.nlp(input_text)
        
        entities = [ent.text.lower() for ent in doc.ents]
        nouns = [token.text.lower() for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities + nouns)
    
    def calculate_cluster_overlap(self, cluster1, cluster2):
        """Calculate overlap between two clusters based on similarity scores"""
        if not cluster1['similarities'] or not cluster2['similarities']:
            return 0
            
        # Get top 10 most similar articles for each cluster
        cluster1_articles = set()
        cluster2_articles = set()
        
        # Sort similarities by value in descending order and take top 10
        sorted_similarities1 = sorted(
            cluster1['similarities'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        sorted_similarities2 = sorted(
            cluster2['similarities'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Extract just the article indices
        cluster1_articles = {idx for idx, _ in sorted_similarities1}
        cluster2_articles = {idx for idx, _ in sorted_similarities2}
        
        # Calculate overlap as percentage of articles that could belong to both clusters
        overlap = len(cluster1_articles & cluster2_articles)
        min_size = min(len(cluster1_articles), len(cluster2_articles))
        return overlap / min_size if min_size > 0 else 0
    
    def merge_similar_clusters(self, clusters):
        """Merge clusters that share more than threshold of their potential articles"""
        merged = True
        while merged:
            merged = False
            cluster_ids = list(clusters.keys())
            
            for i in range(len(cluster_ids)):
                for j in range(i + 1, len(cluster_ids)):
                    
                    c1_id, c2_id = cluster_ids[i], cluster_ids[j]
                    
                    if c1_id not in clusters or c2_id not in clusters:
                        continue
                    
                    overlap = self.calculate_cluster_overlap(
                        clusters[c1_id],
                        clusters[c2_id]
                    )
                    
                    if overlap >= self.merge_threshold:
                        try:
                            if len(clusters[c1_id]['articles']) >= len(
                                clusters[c2_id]['articles']
                            ):
                                self.logger.info(f"Merging cluster {c2_id} into {c1_id}")
                                # Add subdocument before merging
                                if 'subdocuments' not in clusters[c1_id]:
                                    clusters[c1_id]['subdocuments'] = []
                                clusters[c1_id]['subdocuments'].append(
                                    (clusters[c2_id]['doc_index'], 
                                     len(clusters[c2_id]['articles']))
                                )

                                if 'subdocuments' in clusters[c2_id]:
                                    clusters[c1_id]['subdocuments'].extend(
                                        clusters[c2_id]['subdocuments']
                                    )
                                # Merge similarities
                                for idx, sim in clusters[c2_id]['similarities'].items():
                                    if idx not in clusters[c1_id]['similarities'] or \
                                    sim > clusters[c1_id]['similarities'][idx]:
                                        clusters[c1_id]['similarities'][idx] = sim
                                
                                clusters[c1_id]['articles'].extend(
                                    clusters[c2_id]['articles']
                                )
                                clusters[c1_id]['articles'] = list(
                                    set(clusters[c1_id]['articles'])
                                )
                                del clusters[c2_id]

                                self.logger.info(f"New cluster has {len(clusters[c1_id]['articles'])} articles")
                            else:
                                self.logger.info(f"Merging cluster {c1_id} into {c2_id}")
                                # Add subdocument before merging
                                if 'subdocuments' not in clusters[c2_id]:
                                    clusters[c2_id]['subdocuments'] = []
                                clusters[c2_id]['subdocuments'].append(
                                    (clusters[c1_id]['doc_index'], 
                                     len(clusters[c1_id]['articles']))
                                )

                                if 'subdocuments' in clusters[c1_id]:
                                    clusters[c2_id]['subdocuments'].extend(
                                        clusters[c1_id]['subdocuments']
                                    )
                                
                                # Merge similarities
                                for idx, sim in clusters[c1_id]['similarities'].items():
                                    if idx not in clusters[c2_id]['similarities'] or \
                                    sim > clusters[c2_id]['similarities'][idx]:
                                        clusters[c2_id]['similarities'][idx] = sim
                                
                                clusters[c2_id]['articles'].extend(
                                    clusters[c1_id]['articles']
                                )
                                clusters[c2_id]['articles'] = list(
                                    set(clusters[c2_id]['articles'])
                                )
                                del clusters[c1_id]

                                self.logger.info(f"New cluster has {len(clusters[c2_id]['articles'])} articles")
                            merged = True
                            break
                        except Exception as e:
                            self.logger.error(f"Error merging clusters {c1_id} and {c2_id}: {e}")
                if merged:
                    break
        
        return clusters
    
    def create_initial_clusters(self, gov_embeddings, news_embeddings):
        """Create initial clusters based on government documents"""
        clusters = {}
        used_articles = set()
        
        # First pass: Create clusters and find all potential article matches
        for i, doc_embedding in enumerate(gov_embeddings):
            cluster_articles = []
            for j, news_embedding in enumerate(news_embeddings):
                similarity = np.dot(doc_embedding, news_embedding) / (
                    np.linalg.norm(doc_embedding) * np.linalg.norm(news_embedding)
                )
                if similarity >= self.similarity_threshold:
                    cluster_articles.append((j, similarity))
            
            if cluster_articles:
                clusters[i] = {
                    'doc_index': i,
                    'articles': [],
                    'similarities': {}
                }
                for article_idx, similarity in cluster_articles:
                    clusters[i]['similarities'][article_idx] = similarity
        
        self.logger.info(f"Created {len(clusters)} initial clusters")
        # Second pass: Assign articles to clusters based on highest similarity
        for article_idx in range(len(news_embeddings)):
            max_similarity = -1
            best_cluster = None
            
            for cluster_id, cluster_data in clusters.items():
                if article_idx in cluster_data['similarities']:
                    similarity = cluster_data['similarities'][article_idx]
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_cluster = cluster_id
            
            if best_cluster is not None and article_idx not in used_articles:
                clusters[best_cluster]['articles'].append(article_idx)
                used_articles.add(article_idx)
        
        self.logger.info(f"Assigned {len(used_articles)} articles to clusters")
        
        return clusters
    
    def calculate_cluster_score(self, cluster):
        """Calculate cluster score based on average similarity, merged gov docs, and article count"""
        if not cluster['articles']:
            return 0
            
        # Get top 3 articles by similarity
        sorted_articles = sorted(
            cluster['articles'],
            key=lambda x: cluster['similarities'][x],
            reverse=True
        )[:5]
        
        # Calculate average similarity of top 3 articles
        avg_similarity = sum(
            cluster['similarities'][idx] for idx in sorted_articles
        ) / min(3, len(sorted_articles))
        
        # Calculate normalized article count (assuming max 100 articles)
        norm_article_count = len(cluster['articles']) / 100

        # Secondary gov docs count
        if 'subdocuments' in cluster:
            subdoc_count = len(cluster['subdocuments']) / 10
        else:
            subdoc_count = 0
        
        # Calculate final score
        score = 2 * avg_similarity + 0.4 * norm_article_count + 0.6 * subdoc_count
        return score

    
    def create_cluster_dataframes(self, clusters, news_df, gov_df):
        """Create metadata for each cluster including dataframe, center, and score"""
        # Rank clusters by score
        ranked_clusters = []
        for cluster_id, cluster_data in clusters.items():
            score = self.calculate_cluster_score(cluster_data)
            ranked_clusters.append((cluster_id, cluster_data, score))
        
        # Sort clusters by score in descending order
        ranked_clusters.sort(key=lambda x: x[2], reverse=True)
        
        cluster_metadata = []

        try:
            for rank, (cluster_id, cluster_data, score) in enumerate(ranked_clusters, 1):
                rows = []
                embeddings = []
                
                # Add primary document
                doc_idx = cluster_data['doc_index']
                main_keyword = gov_df.iloc[doc_idx]['keyword']
                
                rows.append({
                    'source': 'gov',
                    'type': 'primary', 
                    'title': gov_df.iloc[doc_idx]['title'],
                    'text': gov_df.iloc[doc_idx]['full_text'][100:],
                    'url': gov_df.iloc[doc_idx]['url'],
                    'keyword': main_keyword,
                })
                embeddings.append(gov_df.iloc[doc_idx]['embeddings'])
                
                # Add subdocuments if they exist
                if 'subdocuments' in cluster_data and cluster_data['subdocuments']:
                    sorted_subdocs = sorted(
                        cluster_data['subdocuments'],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for subdoc_idx, doc_count in sorted_subdocs[:5]:
                        rows.append({
                            'source': 'gov',
                            'type': 'secondary',
                            'title': gov_df.iloc[subdoc_idx]['title'],
                            'text': gov_df.iloc[subdoc_idx]['full_text'],
                            'url': gov_df.iloc[subdoc_idx]['url'],
                            'keyword': gov_df.iloc[subdoc_idx]['keyword'],
                        })
                    embeddings.append(gov_df.iloc[subdoc_idx]['embeddings'])
                
                # Add news articles
                sorted_articles = sorted(
                    cluster_data['articles'],
                    key=lambda x: cluster_data['similarities'][x],
                    reverse=True
                )
                
                # Add top news article text
                for article_idx in sorted_articles[:5]:  # Use top 5 articles
                    article = news_df.iloc[article_idx]
                    embeddings.append(news_df.iloc[article_idx]['embeddings'])
                    rows.append({
                        'source': 'gnews',
                        'type': 'news',
                        'title': article['title'],
                        'text': article['full_text'],
                        'url': article['url'],
                        'keyword': article['keyword'],
                    })
                
                # Calculate center as mean of all embeddings
                center_embedding = np.mean(embeddings, axis=0)

                # Create cluster metadata
                cluster_metadata.append({
                    'center_embedding': center_embedding.tolist(),
                    'articles': pd.DataFrame(rows).to_json()
                })
                
        except Exception as e:
            self.logger.error(f"Error processing clusters: {e}")

        return cluster_metadata

    def cluster_articles(self, news_df, gov_df):
        """Main method to cluster articles and generate report"""
        try:
            if news_df.empty:
                self.logger.error("No Google News articles found")
            
            if gov_df.empty:
                self.logger.error("No federal documents found")
            
            # Embed Google News article titles
            self.logger.info(f"Embedding {len(news_df)} Google News article titles...")
            news_titles = news_df['title'].tolist()
            news_embeddings = self.model.embed(news_titles, model = "voyage-3.5-lite", input_type="document").embeddings

            # Embed federal documents
            self.logger.info(f"Embedding {len(gov_df)} government document titles...")
            gov_texts = []
            for index, row in gov_df.iterrows():
                title = row['title']
                text = row['full_text']
                content = title + " " + self.extract_entities(text[1000:10000])
                gov_texts.append(content[:5000])
            
            gov_embeddings = self.model.embed(gov_texts, model = "voyage-3.5-lite", input_type="document").embeddings

            # Create and merge clusters
            clusters = self.create_initial_clusters(gov_embeddings, news_embeddings)

            self.logger.info(f"Number of clusters before merge: {len(clusters)}")
            clusters = self.merge_similar_clusters(clusters)

            self.logger.info(f"Final number of clusters: {len(clusters)}")
            
            # add embeddings to dfs
            news_df['embeddings'] = news_embeddings
            gov_df['embeddings'] = gov_embeddings
            # Create dataframes
            dfs = self.create_cluster_dataframes(clusters, news_df, gov_df)
            
            return dfs
        except Exception as e:
            self.logger.error(f"Error in clustering process: {e}")


def load_df(type):
    # Initialize S3 client
    s3 = boto3.client('s3')
    astra_bucket_name = os.getenv("ASTRA_BUCKET_NAME")
    try:
        # Load pickled DataFrame from S3
        key = f"{type}/articles.pkl"
        response = s3.get_object(Bucket=astra_bucket_name, Key=key)
        df = pickle.loads(response['Body'].read())
        print(f"Loaded DataFrame with {len(df)} articles")

        return df
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise e  


def handler(payload):

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    news_df = load_df('gnews')
    gov_df = load_df('gov')

    # Create clusterer and run clustering
    clusterer = ArticleClusterer()
    clusters = clusterer.cluster_articles(news_df, gov_df)

    if clusters and len(clusters) > 0:

        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        try:
            for i, metadata in enumerate(clusters):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clusters (embedding, metadata)
                    VALUES (%s, %s::jsonb)
                    RETURNING id
                """, (metadata['center_embedding'], json.dumps(metadata['articles'])))

                print(f"Inserted cluster {i} into db")
        except Exception as e:
            print(f"Error inserting cluster {i} into db: {e}")

    else:
        logging.error("No clusters generated")

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    with open('tmp/gov.pkl', 'rb') as f:
        gov_df = pickle.loads(f.read())
    with open('tmp/gnews.pkl', 'rb') as f:
        news_df = pickle.loads(f.read())

    # Display input dataframes
    print("\n=========== Input DataFrames =============")
    print("\nGoogle News DataFrame (top 5):")
    print(f"Shape: {news_df.shape}")
    print("Columns:", news_df.columns.tolist())
    print("\nSample of news articles:")
    for idx, row in news_df.iterrows():
        print(f"{idx+1}. {row['title']}")
        print(f"URL: {row['url']}")
        print(row['full_text'][:1000])
        if idx >= 4:  # Show first 5 articles
            break 
    
    print("\nGovernment Documents DataFrame (top 5):")
    print(f"Shape: {gov_df.shape}")
    print("Columns:", gov_df.columns.tolist())
    print("\nSample of government documents:")
    for idx, row in gov_df.iterrows():
        print(f"{idx+1}. {row['title']}")
        print(f"URL: {row['url']}")
        print(row['full_text'][:1000])
        if idx >= 4:  # Show first 5 articles
            break


    # Create clusterer and run clustering
    clusterer = ArticleClusterer()
    clusters = clusterer.cluster_articles(news_df, gov_df)
    # with open ('tmp/clusters.pkl', 'rb') as f:
    #    clusters = pickle.load(f)

    if clusters and len(clusters) > 0:
        # save to tmp
        with open ('tmp/clusters.pkl', 'wb') as f:
            pickle.dump(clusters, f)
        
        # save to db
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        try:
            for i, metadata in enumerate(clusters):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clusters (embedding, metadata)
                    VALUES (%s, %s::jsonb)
                    RETURNING id
                """, (metadata['center_embedding'], json.dumps(metadata['articles'])))

                print(f"Inserted cluster {i} into db")
        except Exception as e:
            print(f"Error inserting cluster {i} into db: {e}")

        # print debugging
        print(f"{len(clusters)} clusters created")
        print("========== OUTPUT CLUSTERS ===========")
        for i, metadata in enumerate(clusters):
            print(f"----- Cluster {i+1} -------")
            print(f"Center embedding shape: {metadata['center_embedding'].shape}")
            df = pd.read_json(metadata['articles'])
            print(f"Number of articles: {len(df)}")
            for idx, row in df.head().iterrows():
                print(f"{row['title']}")
                if idx >= 4:
                    break
            print()
    else:
        logging.error("No clusters generated.")

