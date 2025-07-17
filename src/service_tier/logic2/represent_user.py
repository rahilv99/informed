import psycopg2
from sentence_transformers import SentenceTransformer
import os

# Database connection parameters

# db_access_url = os.environ.get('DB_ACCESS_URL')
db_access_url = 'postgresql://postgres.uufxuxbilvlzllxgbewh:astrapodcast!@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

# Load model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')

def main(interests, user_id):
    print("Embedding...")
    embedding = model.encode(interests).tolist()

    vector_str = f"[{','.join(map(str, embedding))}]"
    print("Attempting to insert into user table")
    conn = None
    try:
        conn = psycopg2.connect(db_access_url)
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET embedding = %s WHERE id = %s",
            (vector_str, user_id)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating user embedding: {e}")
    finally:
        if conn:
            conn.close()


def handler(payload):
    user_id = payload.get("user_id")
    interests = payload.get("keywords")
    print(f"represent_user.py invoked with interests: {interests}")

    interests = ' '.join(interests)
    main(interests, user_id)

if __name__ == "__main__":
    interests = ["tariffs", "immigration", "foreign aid"]
    user_id = 27
    print(f"represent_user.py invoked with interests: {interests}")

    interests = ' '.join(interests)
    main(interests, user_id)