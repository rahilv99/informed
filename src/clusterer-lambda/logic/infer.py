import os
import psycopg2
import json
from sentence_transformers import SentenceTransformer

import common.sqs
import common.s3

# Database connection parameters

db_access_url = os.environ.get('DB_ACCESS_URL')

# Load model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')


def search_documents(interest, conn, limit=5):
    query_embedding = model.encode(interest).tolist()
    cur =  conn.cursor() 
    try:
        cur.execute("""
            SELECT id, score, embedding <=> %s::vector AS distance
            FROM articles
            ORDER BY distance
            LIMIT %s
        """, (query_embedding, limit))
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error executing query: {e}")
        return []

def main(interests):
    clusters = {}
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        for interest in interests:
            rows = search_documents(interest, conn)
            for row in rows:
                id, score, distance = row

                if id in clusters:
                    # add this distance to entry for cluster
                    clusters[id][0].append(distance)
                else:
                    clusters[id] = ([distance], score) 
    finally:
        if conn:
            conn.close()

    # sorting
    recommendations = []
    for id, (distances, score) in clusters.items():
        # Lower distance means higher similarity
        dist = min(distances) / len(distances)
        score = dist / max(1, score)
        recommendations.append(score, id)
    
    recommendations.sort(key = lambda x: x[0])
    # only return metadata
    return [id for _, id in recommendations[:5]]


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
    print(f"Recommended article IDs: {recommendations}")

    
    if recommendations and len(recommendations) > 0:
        try:
            # everyone gets a newsletter
            next_event = {
                "action": "e_email",
                "payload": { 
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_name,
                    "plan": plan,
                    "episode": episode,
                    "recommendations": recommendations
                }
            }

            common.sqs.send_to_content_queue(next_event)
            print(f"Sent message to SQS for next action {next_event['action']}")

            if plan != "free":
                next_event = {
                    "action": "e_nlp",
                    "payload": { 
                        "user_id": user_id,
                        "user_name": user_name,
                        "plan": plan,
                        "episode": episode,
                        "ep_type": "pulse",
                        "recommendations": recommendations
                    }
                }

                common.sqs.send_to_content_queue(next_event)
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
            common.sqs.send_to_clusterer_queue(next_event)
            print(f"Sent message to SQS for next action {next_event['action']}")
        except Exception as e:
            print(f"Exception when sending message to SQS {e}")


if __name__ == "__main__":
    interests = ["tariffs", "immigration", "foreign aid"]
    print(f"Infer.py invoked with interests: {interests}")

    recommendations = main(interests)

    if len(recommendations) < 5:
        print('Warning: Low number of recommendations')

    print(f"Recommended article IDs: {recommendations}")