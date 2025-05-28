from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import boto3
import os
import pickle

def add_embeddings(df: pd.DataFrame, title_column: str = 'title') -> pd.DataFrame:
    """
    Add embeddings to a dataframe using all-MiniLM-L6-v2 sentence transformer.
    
    Args:
        df (pd.DataFrame): Input dataframe
        title_column (str): Name of the column containing text to embed (default: 'title')
    
    Returns:
        pd.DataFrame: Dataframe with new 'embeddings' column
    """
    # Initialize the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings for all titles
    embeddings = model.encode(df[title_column].tolist())
    
    # Add embeddings as a new column
    df['embeddings'] = embeddings.tolist()
    
    return df

def handler(payload):
    prefix = payload.get('prefix', 'gnews/')
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    astra_bucket_name = os.getenv("ASTRA_BUCKET_NAME")
    
    try:
        # Load pickled DataFrame from S3
        key = f"{prefix}articles.pkl"
        response = s3.get_object(Bucket=astra_bucket_name, Key=key)
        df = pickle.loads(response['Body'].read())
        print(f"Loaded DataFrame with {len(df)} articles")
        
        # Add embeddings
        df = add_embeddings(df)
        print("Added embeddings to DataFrame")
        
        # Serialize and save back to S3
        serialized_data = pickle.dumps(df)
        s3.put_object(Bucket=astra_bucket_name, Key=key, Body=serialized_data)
        print('Saved DataFrame with embeddings back to S3')
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise e
