"""
Simple semantic clustering for government documents and news articles
with government documents as cluster anchors
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging
import psycopg2
import boto3
import pickle
import os
import json
import spacy

# db_access_url = os.environ.get('DB_ACCESS_URL')
db_access_url = 'postgresql://postgres.uufxuxbilvlzllxgbewh:astrapodcast!@aws-0-us-east-1.pooler.supabase.com:6543/postgres' # local testing


class Clusterer:
    """
    A simple clusterer that groups news articles around government documents
    based on semantic similarity. Each cluster must have at least one government document.
    """
    def __init__(self, similarity_threshold=0.3, merge_threshold=0.8):
        """
        Initialize the clusterer with similarity thresholds.
        
        Parameters:
        - similarity_threshold: Minimum similarity for assigning news to gov docs (0-1)
        - merge_threshold: Threshold for merging similar government documents (0-1)
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.nlp = spacy.load("en_core_web_sm")
        self.similarity_threshold = similarity_threshold
        self.merge_threshold = merge_threshold
    
    def extract_entities(self, input_text):
        """Extract entities and nouns from text"""
        if not isinstance(input_text, str):
            return ""
        
        doc = self.nlp(input_text)
        
        entities = [ent.text.lower() for ent in doc.ents]
        nouns = [token.text.lower() for token in doc if token.pos_ == "NOUN"]
        return " ".join(entities + nouns)
    
    def prepare_documents(self, gov_df, news_df):
        """
        Prepare government documents and news articles for embedding.
        
        Parameters:
        - gov_df: DataFrame containing government documents
        - news_df: DataFrame containing news articles
        
        Returns:
        - gov_texts: List of government document texts for embedding
        - news_texts: List of news article texts for embedding
        """
        gov_texts = []
        news_texts = []
        
        # Process government documents
        for _, row in gov_df.iterrows():
            # Use title and beginning of text
            title = row['title']
            text = row.get('text', '')
            sz = len(text)
            mid = sz // 2
            content = title + " " + self.extract_entities(text[mid:mid+5000]) # get text somewhere in the middle
            gov_texts.append(content[:200])
        
        # Process news articles
        for _, row in news_df.iterrows():
            # Use title and beginning of text
            text = row['title']
            news_texts.append(text)
        
        return gov_texts, news_texts
    
    def generate_embeddings(self, gov_texts, news_texts):
        """
        Generate embeddings for government documents and news articles.
        
        Parameters:
        - gov_texts: List of government document texts
        - news_texts: List of news article texts
        
        Returns:
        - gov_embeddings: Array of government document embeddings
        - news_embeddings: Array of news article embeddings
        """
        print(f"Generating embeddings for {len(gov_texts)} government documents...")
        gov_embeddings = self.model.encode(gov_texts)
        
        print(f"Generating embeddings for {len(news_texts)} news articles...")
        news_embeddings = self.model.encode(news_texts)
        
        print(f"Generated {len(gov_embeddings)} government document embeddings and {len(news_embeddings)} news article embeddings")
        return gov_embeddings, news_embeddings
    
    def calculate_similarities(self, gov_embeddings, news_embeddings):
        """
        Calculate similarities between government documents and news articles.
        
        Parameters:
        - gov_embeddings: Array of government document embeddings
        - news_embeddings: Array of news article embeddings
        
        Returns:
        - gov_news_sim: Similarity matrix between government documents and news articles
        - gov_gov_sim: Similarity matrix between government documents
        """
        # Calculate similarity between government documents and news articles
        gov_news_sim = cosine_similarity(gov_embeddings, news_embeddings)
        
        # Calculate similarity between government documents
        gov_gov_sim = cosine_similarity(gov_embeddings)
        
        return gov_news_sim, gov_gov_sim
    
    def merge_similar_gov_docs(self, gov_gov_sim):
        """
        Merge similar government documents into clusters using a more efficient approach.
        
        Parameters:
        - gov_gov_sim: Similarity matrix between government documents
        
        Returns:
        - gov_clusters: Dictionary mapping cluster IDs to lists of government document indices
        """
        n_gov = gov_gov_sim.shape[0]
        
        # Initialize each government document as its own cluster
        gov_clusters = {i: [i] for i in range(n_gov)}
        
        # Create a priority queue of similarities
        similarities = []
        for i in range(n_gov):
            for j in range(i + 1, n_gov):
                sim = gov_gov_sim[i, j]
                if sim >= self.merge_threshold:
                    similarities.append((-sim, i, j))  # Negative for max-heap
        
        # Sort once to create a max-heap
        similarities.sort()  # Will sort by first element (-sim)
        
        # Track which cluster ID each document belongs to
        doc_to_cluster = {i: i for i in range(n_gov)}
        
        while similarities:
            sim, doc1, doc2 = similarities.pop(0)
            sim = -sim  # Convert back to positive
            
            # Get current cluster IDs
            c1_id = doc_to_cluster[doc1]
            c2_id = doc_to_cluster[doc2]
            
            # Skip if documents are already in the same cluster
            if c1_id == c2_id:
                continue
                
            # Merge smaller cluster into larger one
            if len(gov_clusters[c1_id]) < len(gov_clusters[c2_id]):
                c1_id, c2_id = c2_id, c1_id
                
            print(f"Merging clusters {c2_id} into {c1_id} with similarity {sim:.4f}")
            
            # Update cluster assignments
            for doc_idx in gov_clusters[c2_id]:
                doc_to_cluster[doc_idx] = c1_id
            
            # Merge clusters
            gov_clusters[c1_id].extend(gov_clusters[c2_id])
            del gov_clusters[c2_id]
        
        print(f"Created {len(gov_clusters)} government document clusters")
        return gov_clusters

    def assign_news_to_gov_clusters(self, gov_clusters, gov_news_sim):
        """
        Assign news articles to government document clusters, with a maximum of 10 news articles per cluster.
        
        Parameters:
        - gov_clusters: Dictionary mapping cluster IDs to lists of government document indices
        - gov_news_sim: Similarity matrix between government documents and news articles
        
        Returns:
        - final_clusters: Dictionary mapping cluster IDs to dictionaries containing gov docs and news articles
        """
        n_news = gov_news_sim.shape[1]
        final_clusters = {}
        
        # Initialize final clusters with government documents
        for cluster_id, gov_indices in gov_clusters.items():
            final_clusters[cluster_id] = {
                'gov_indices': gov_indices,
                'news_indices': [],
                'news_similarities': {}
            }
        
        # For each news article, find the most similar government document clusters
        for news_idx in range(n_news):
            # Store all cluster similarities for this news article
            cluster_similarities = []
            
            for cluster_id, cluster_data in final_clusters.items():
                # Calculate average similarity to all government documents in the cluster
                cluster_sim = 0
                for gov_idx in cluster_data['gov_indices']:
                    cluster_sim += gov_news_sim[gov_idx, news_idx]
                
                avg_sim = cluster_sim / len(cluster_data['gov_indices'])
                
                if avg_sim >= self.similarity_threshold:
                    cluster_similarities.append((cluster_id, avg_sim))
            
            # Sort clusters by similarity (descending)
            cluster_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Try to assign to the most similar cluster that isn't full
            for cluster_id, sim in cluster_similarities:
                if len(final_clusters[cluster_id]['news_indices']) < 10:
                    final_clusters[cluster_id]['news_indices'].append(news_idx)
                    final_clusters[cluster_id]['news_similarities'][news_idx] = sim
                    break
        
        # Count assigned news articles
        total_assigned = sum(len(cluster['news_indices']) for cluster in final_clusters.values())
        print(f"Assigned {total_assigned}/{n_news} news articles to clusters")
        
        return final_clusters
    
    def organize_clusters(self, final_clusters, gov_df, news_df, gov_embeddings):
        """
        Organize clusters for output.
        
        Parameters:
        - final_clusters: Dictionary mapping cluster IDs to dictionaries containing gov docs and news articles
        - gov_df: DataFrame containing government documents
        - news_df: DataFrame containing news articles
        
        Returns:
        - organized_clusters: List of organized cluster dictionaries
        """
        organized_clusters = []
        
        for cluster_id, cluster_data in final_clusters.items():

            cluster_gov_embeddings = gov_embeddings[cluster_data['gov_indices']]
            center_embedding = np.mean(cluster_gov_embeddings, axis=0)

            # Create cluster
            cluster = {
                'id': cluster_id,
                'documents': [],
                'gov_count': len(cluster_data['gov_indices']),
                'news_count': len(cluster_data['news_indices']),
                'total_count': len(cluster_data['gov_indices']) + len(cluster_data['news_indices']),
                'center_embedding': center_embedding.tolist() 
            }
            
            # Add government documents
            for gov_idx in cluster_data['gov_indices']:
                cluster['documents'].append({
                    'source': 'gov',
                    'type': 'primary',
                    'title': gov_df.iloc[gov_idx]['title'],
                    'text': gov_df.iloc[gov_idx].get('full_text', ''),
                    'url': gov_df.iloc[gov_idx].get('url', ''),
                    'keyword': gov_df.iloc[gov_idx].get('keyword', '')
                })
            
            # Add news articles, sorted by similarity
            if cluster_data['news_indices']:
                sorted_news = sorted(
                    [(idx, cluster_data['news_similarities'].get(idx, 0)) 
                     for idx in cluster_data['news_indices']],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for news_idx, sim in sorted_news:
                    cluster['documents'].append({
                        'source': 'gnews',
                        'type': 'news',
                        'title': news_df.iloc[news_idx]['title'],
                        'text': news_df.iloc[news_idx].get('full_text', ''),
                        'url': news_df.iloc[news_idx].get('url', ''),
                        'keyword': news_df.iloc[news_idx].get('keyword', ''),
                        'similarity': float(f"{sim:.4f}")
                    })
            
            organized_clusters.append(cluster)
        
        # Sort clusters by total document count (descending)
        organized_clusters.sort(key=lambda x: x['total_count'], reverse=True)
        
        return organized_clusters
    
    def format_output(self, organized_clusters):
        """
        Format clusters for output.
        
        Parameters:
        - organized_clusters: List of organized cluster dictionaries
        
        Returns:
        - output: List of formatted cluster metadata
        """
        output = []
        
        for cluster in organized_clusters:
            # Create a dataframe from the documents
            df = pd.DataFrame(cluster['documents'])
            
            # Calculate a simple score based on document count and government document count
            score = 1.0 + min(cluster['total_count'] / 10, 1.0) + (cluster['gov_count'] * 0.2)
            
            # Create metadata
            metadata = {
                'center_embedding': cluster['center_embedding'],
                'score': float(f"{score:.4f}"),
                'articles': df.to_json()
            }
            
            output.append(metadata)
        
        return output
    
    def generate_metrics_report(self, organized_clusters, gov_df, news_df, output_path="tmp/cluster_metrics_report.txt"):
        """
        Generate a metrics report for clusters and save to a text file.
        
        Parameters:
        - organized_clusters: List of organized cluster dictionaries as returned by organize_clusters.
        - gov_df: DataFrame containing government documents.
        - news_df: DataFrame containing news articles.
        - output_path: Path for the output text file.
        """
        total_clusters = len(organized_clusters)
        total_gov = len(gov_df)
        total_news = len(news_df)
        
        report_lines = []
        report_lines.append("=== Cluster Metrics Report ===\n")
        report_lines.append(f"Total clusters: {total_clusters}\n")
        report_lines.append(f"Total government documents: {total_gov}\n")
        report_lines.append(f"Total news articles: {total_news}\n")
        report_lines.append("-" * 40 + "\n")
        
        for cluster in organized_clusters:
            cluster_id = cluster.get('id', 'N/A')
            gov_count = cluster.get('gov_count', 0)
            news_count = cluster.get('news_count', 0)
            total_count = cluster.get('total_count', 0)
            
            # Attempt to compute news similarity stats if available
            similarities = []
            # We need to extract similarity values from news documents if present
            for doc in cluster.get('documents', []):
                if doc.get('source') == 'gnews' and 'similarity' in doc:
                    similarities.append(doc['similarity'])
            
            if similarities:
                avg_sim = sum(similarities) / len(similarities)
                max_sim = max(similarities)
                min_sim = min(similarities)
            else:
                avg_sim = max_sim = min_sim = 0
            
            # Aggregate keywords from government documents
            keywords = []
            for doc in cluster.get('documents', []):
                if doc.get('source') == 'gov':
                    kw = doc.get('keyword', "")
                    if kw:
                        keywords.append(kw)
            unique_keywords = list(set(keywords))
            
            # Include cluster score if present from format_output metadata
            cluster_score = cluster.get('score', "N/A")
            
            report_lines.append(f"Cluster ID: {cluster_id}")
            report_lines.append(f"  Total documents: {total_count} (Gov: {gov_count}, News: {news_count})")
            report_lines.append(f"  Cluster score: {cluster_score}")
            if similarities:
                report_lines.append(f"  News similarity (avg/max/min): {avg_sim:.4f} / {max_sim:.4f} / {min_sim:.4f}")
            else:
                report_lines.append("  No news similarity metrics available.")
            if unique_keywords:
                report_lines.append(f"  Aggregated Keywords: {', '.join(unique_keywords)}")
            else:
                report_lines.append("  No keywords available.")
            report_lines.append("-" * 40 + "\n")
        
        # try:
        #     with open(output_path, "w") as f:
        #         f.writelines(line + "\n" for line in report_lines)
        #     print(f"Metrics report saved to {output_path}")
        # except Exception as e:
        #     print(f"Error writing metrics report: {e}")
        
    def cluster_articles(self, news_df, gov_df):
        """
        Main method to cluster articles and generate report.
        
        Parameters:
        - news_df: DataFrame containing news articles
        - gov_df: DataFrame containing government documents
        
        Returns:
        - output: List of cluster metadata
        """
        try:
            if gov_df.empty:
                print("No government documents to anchor clusters")
                return []
            
            if news_df.empty:
                print("No news articles to cluster")
                # Still create clusters with just government documents
                news_df = pd.DataFrame(columns=['title', 'full_text', 'url', 'keyword'])
            
            # Step 1: Prepare documents
            gov_texts, news_texts = self.prepare_documents(gov_df, news_df)
            
            # Step 2: Generate embeddings
            gov_embeddings, news_embeddings = self.generate_embeddings(gov_texts, news_texts)
            
            # Step 3: Calculate similarities
            gov_news_sim, gov_gov_sim = self.calculate_similarities(gov_embeddings, news_embeddings)
            
            # Step 4: Merge similar government documents
            gov_clusters = self.merge_similar_gov_docs(gov_gov_sim)
            
            # Step 5: Assign news articles to government document clusters
            final_clusters = self.assign_news_to_gov_clusters(gov_clusters, gov_news_sim)
            
            # Step 6: Organize clusters
            organized_clusters = self.organize_clusters(final_clusters, gov_df, news_df, gov_embeddings)
            
            # Step 7: Format output
            output = self.format_output(organized_clusters)
            
            # Print summary
            print("========== CLUSTERING SUMMARY ===========")
            print(f"Total government documents: {len(gov_df)}")
            print(f"Total news articles: {len(news_df)}")
            print(f"Total clusters created: {len(organized_clusters)}")
            
            gov_in_clusters = sum(cluster['gov_count'] for cluster in organized_clusters)
            news_in_clusters = sum(cluster['news_count'] for cluster in organized_clusters)
            
            print(f"Government documents in clusters: {gov_in_clusters}/{len(gov_df)} ({gov_in_clusters/max(1, len(gov_df))*100:.1f}%)")
            print(f"News articles in clusters: {news_in_clusters}/{len(news_df)} ({news_in_clusters/max(1, len(news_df))*100:.1f}%)")
            
            print("========== OUTPUT CLUSTERS ===========")
            for i, cluster in enumerate(organized_clusters[:10]):  # Show top 10 clusters
                print(f"----- Cluster {i+1} -------")
                print(f"Documents: {cluster['total_count']} ({cluster['gov_count']} gov, {cluster['news_count']} news)")
                for j, doc in enumerate(cluster['documents'][:5]):  # Show top 5 documents
                    print(f"{doc['source']}: {doc['title']}")
                    if j >= 4:
                        break
                print()
            
            # Generate metrics report
            self.generate_metrics_report(organized_clusters, gov_df, news_df)
            
            return output
            
        except Exception as e:
            logging.error(f"Error in clustering: {e}")
            return []


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
    
# AWS Lambda handler function
def handler(payload):
    """AWS Lambda handler for article clustering"""
    logging.info("Starting simple semantic clustering Lambda function")
    
    news_df = load_df('gnews')
    gov_df = load_df('gov')
    
    clusterer = Clusterer()
    clusters = clusterer.cluster_articles(news_df, gov_df)
    
    if clusters and len(clusters) > 0:

        # save to db
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')

        try:
            # Delete all existing entries first
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clusters")
            conn.commit()  
            print("Deleted all existing clusters from db")

            for i, metadata in enumerate(clusters):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clusters (embedding, score, metadata)
                    VALUES (%s, %s, %s::jsonb)
                    RETURNING id
                """, (metadata['center_embedding'], metadata['score'], json.dumps(metadata['articles'])))
            conn.commit()
            print(f"Inserted {len(clusters)} clusters into db")
        except Exception as e:
            print(f"Error inserting clusters into db: {e}")
            conn.rollback()
        finally:
            conn.close()
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

    clusterer = Clusterer()
    clusters = clusterer.cluster_articles(news_df, gov_df)
    
    if clusters and len(clusters) > 0:

        # save to db
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')

        try:
            # Delete all existing entries first
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clusters")
            conn.commit()
            print("Deleted all existing clusters from db")

            for i, metadata in enumerate(clusters):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clusters (embedding, score, metadata)
                    VALUES (%s, %s, %s::jsonb)
                    RETURNING id
                """, (metadata['center_embedding'], metadata['score'], json.dumps(metadata['articles'])))
            conn.commit()
            print(f"Inserted {len(clusters)} clusters into db")
        except Exception as e:
            print(f"Error inserting clusters into db: {e}")
            conn.rollback()
        finally:
            conn.close()
    else:
        logging.error("No clusters generated")
