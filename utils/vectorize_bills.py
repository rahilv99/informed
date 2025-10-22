#!/usr/bin/env python3

import os
import sys
from google import genai
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import spacy

# Add the parent directory to the Python path so we can import common_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

nlp = spacy.load("en_core_web_sm")

import common_utils.database as database

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
uri = os.environ.get("DB_URI")

genai_client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_entities(input_text):
    """Extract entities and nouns from text"""
    if not isinstance(input_text, str):
        return ""
    
    # trim for spacy limit
    input_text = input_text[:50000]
    doc = nlp(input_text)
    
    entities = [ent.text.lower() for ent in doc.ents]
    nouns = [token.text.lower() for token in doc if token.pos_ == "NOUN"]
    return " ".join(entities + nouns)

def get_embedding(content):
    """
    Generate embedding vector for the given content using Google's Gemini embedding model.
    
    Args:
        content (str): Text content to vectorize
    
    Returns:
        list: Normalized embedding vector (768 dimensions)
    """
    result = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=content,
        config=genai.types.EmbedContentConfig(output_dimensionality=768)
    )

    [embedding_obj] = result.embeddings
    embedding_values_np = np.array(embedding_obj.values)
    normed_embedding = embedding_values_np / np.linalg.norm(embedding_values_np)

    return normed_embedding.tolist()


def vectorize_bill_text(bill):
    """
    Vectorize the text attribute of a bill after entity extraction.
    
    Args:
        bill (dict): Bill document from database
    
    Returns:
        dict: Bill update data with embedding, or None if text is missing
    """
    bill_id = bill.get('bill_id')
    text = bill.get('text')
    title = bill.get('title')
    people = ' '.join([person.get('name', '') for person in bill.get('people', [])]) if bill.get('people', []) else ''
    summary = bill.get('summary', '')

    text = extract_entities(text)
    full_text = f"{title}\n\n{summary}\n\n{people}\n\n{text}"
    
    if not full_text or len(full_text.strip()) == 0:
        print(f"Warning: Bill {bill_id} has no text content. Skipping.")
        return None
    
    print(f"Vectorizing bill {bill_id} (text length: {len(full_text)} chars). Originally {len(bill.get('text', ''))} chars.")
    
    try:
        # Generate embedding for the bill text
        embedding = get_embedding(full_text)
        
        # Return update data
        return {
            'bill_id': bill_id,
            'text_embedding': embedding
        }
    except Exception as e:
        print(f"Error vectorizing bill {bill_id}: {e}")
        return None


def vectorize_all_bills(offset = 564):
    """
    Loop through all bills in the collection and vectorize their text attributes.
    
    Args:
        preview (bool): If True, only show what would be processed without updating
        limit (int): Optional limit on number of bills to process
    
    Returns:
        dict: Summary of processing results
    """
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        return {'success': False, 'error': 'Missing GOOGLE_API_KEY'}
    
    if not uri:
        print("Error: DB_URI environment variable is not set.")
        return {'success': False, 'error': 'Missing DB_URI'}
    
    # Connect to database
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    if not database.test_connection(client):
        print("Failed to connect to MongoDB. Exiting.")
        return {'success': False, 'error': 'Database connection failed'}
    
    db = client['auxiom_database']
    bills_collection = db['bills']
    
    # Get all bills from database
    print("Fetching all bills from database...")
    bills = database.get_all_bills(bills_collection)
    
    if not bills:
        print("No bills found in database.")
        client.close()
        return {'success': True, 'processed': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    
    total_bills = len(bills)
    
    print(f"Processing {total_bills} bills")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    print('starting from ', offset)
    for i, bill in enumerate(bills[offset:], offset+1):
        bill_id = bill.get('bill_id', 'unknown')
        print(f"\n[{i}/{len(bills)}] Processing bill {bill_id}")
        
        # Check if already has embedding
        if bill.get('text_embedding'):
            print(f"Bill {bill_id} already has text_embedding. Skipping.")
            skipped_count += 1
            continue
        
        # Vectorize the bill text
        update_data = vectorize_bill_text(bill)
        
        if update_data:
            # Update the database
            success = database.update_bill(bills_collection, update_data)
            if success:
                print(f"Successfully updated bill {bill_id} with text embedding")
                updated_count += 1
            else:
                print(f"Failed to update bill {bill_id}")
                error_count += 1
        else:
            skipped_count += 1
    
    # Close database connection
    client.close()
    
    print("\n" + "=" * 60)
    print("Vectorization Complete")
    print("=" * 60)
    print(f"Total bills processed: {len(bills)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Skipped (no text or already has embedding): {skipped_count}")
    print(f"Errors: {error_count}")
    
    return {
        'success': True,
        'processed': len(bills),
        'updated': updated_count,
        'skipped': skipped_count,
        'errors': error_count
    }


if __name__ == "__main__":
    vectorize_all_bills()
