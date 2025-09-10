"""
Congress bill embedding generation module
"""

import psycopg2
import os
from sentence_transformers import SentenceTransformer

db_access_url = os.environ.get('DB_ACCESS_URL')

def generate_congress_bill_embeddings():
    """
    Generate embeddings for congress bills that have placeholder embeddings.
    """
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        # Find bills with placeholder embeddings (all zeros)
        cursor.execute("""
            SELECT id, bill_id, title, latest_action_text
            FROM congress_bills
            WHERE embedding = %s
        """, (f"[{','.join(['0'] * 384)}]",))
        
        bills_to_update = cursor.fetchall()
        
        if not bills_to_update:
            print("No congress bills need embedding generation")
            return
        
        print(f"Generating embeddings for {len(bills_to_update)} congress bills")
        
        # Initialize the embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        updated_count = 0
        for bill_id, bill_identifier, title, latest_action_text in bills_to_update:
            try:
                # Generate embedding for the bill
                bill_text = f"{title} {latest_action_text or ''}"
                embedding = model.encode(bill_text).tolist()
                embedding_str = f"[{','.join(map(str, embedding))}]"
                
                # Update the bill with real embedding
                cursor.execute("""
                    UPDATE congress_bills
                    SET embedding = %s
                    WHERE id = %s
                """, (embedding_str, bill_id))
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error generating embedding for bill {bill_identifier}: {e}")
                continue
        
        conn.commit()
        print(f"Successfully generated embeddings for {updated_count} congress bills")
        
    except Exception as e:
        print(f"Error generating congress bill embeddings: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def handler(payload):
    """AWS Lambda handler for congress bill embedding generation"""
    print("Starting congress bill embedding generation")
    generate_congress_bill_embeddings()
    return {"statusCode": 200, "body": "Congress bill embeddings generated successfully"}
