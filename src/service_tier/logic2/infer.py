import psycopg2
import json
from sentence_transformers import SentenceTransformer
from contextlib import contextmanager

# import common.sqs
# import common.s3

# Database connection parameters
db_access_url = 'postgresql://postgres.uufxuxbilvlzllxgbewh:astrapodcast!@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

# Load model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            dsn=db_access_url,
            client_encoding='utf8',
            connect_timeout=10  # Add timeout
        )
        yield conn
    finally:
        if conn is not None:
            conn.close()

def search_documents(interest, limit=5):
    query_embedding = model.encode(interest).tolist()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    SELECT id, metadata, score, embedding <=> %s::vector AS distance
                    FROM clusters
                    ORDER BY distance
                    LIMIT %s
                """, (query_embedding, limit))
                return cur.fetchall()
            except psycopg2.Error as e:
                print(f"Error executing query: {e}")
                return []

def main(interests):
    clusters = {}
    for interest in interests:
        rows = search_documents(interest)
        for row in rows:
            id, metadata, score, distance = row

            if id in clusters:
                # add this distance to entry for cluster
                clusters[id][0].append(distance)
            else:
                clusters[id] = ([distance], score, metadata) 
    
    # sorting
    recommendations = []
    for id, (distances, score, metadata) in clusters.items():
        # Lower distance means higher similarity
        dist = min(distances) / len(distances)
        score = dist / max(1, score)
        recommendations.append((score, metadata))
    
    recommendations.sort(key = lambda x: x[0])
    # only return metadata
    return [metadata for score, metadata in recommendations]


def handler(payload):
    user_id = payload.get("user_id")
    user_email = payload.get("user_email")
    plan = payload.get("plan")
    episode = payload.get("episode")
    interests = payload.get("keywords", [])
    user_name = payload.get("user_name")
    print(f"Infer.py invoked with interests: {interests}")

    recommendations = main(interests)

    if len(recommendations) < 5:
        print('Warning: Low number of recommendations')
    for i, metadata in enumerate(recommendations):
        print(f"------ CLUSTER {i} --------")
        print(metadata)

    
    if recommendations and len(recommendations) > 0:
        common.s3.save_serialized(user_id, episode, "PULSE", {
                "cluster_dfs": recommendations,
        })

        # Send message to SQS
        try:
            next_event = {
                "action": "e_nlp",
                "payload": { 
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name,
                "plan": plan,
                "episode": episode,
                "ep_type": "pulse"
                }
            }
            common.sqs.send_to_sqs(next_event)
            print(f"Sent message to SQS for next action {next_event['action']}")
        except Exception as e:
            print(f"Exception when sending message to SQS {e}")
    else:
        print("No clusters generated, notifying user.")
        # Notify user via email if no clusters generated
        try:
            next_event = {
                "action": "e_notify",
                "payload": { 
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name,
                "keywords": interests
                }
            }
            common.sqs.send_to_sqs(next_event)
            print(f"Sent message to SQS for next action {next_event['action']}")
        except Exception as e:
            print(f"Exception when sending message to SQS {e}")


if __name__ == "__main__":
    interests = ["tariffs", "immigration", "foreign aid"]
    print(f"Infer.py invoked with interests: {interests}")

    recommendations = main(interests)

    for i, metadata in enumerate(recommendations):
        print(f"------ CLUSTER {i} --------")
        # access first title
        data = json.loads(metadata)
        title = data.get("title").get("0")
        print(title)