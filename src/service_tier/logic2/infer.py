import psycopg2
import voyageai
import os

# Connect to the database
db_access_url = os.environ.get('DB_ACCESS_URL')
conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
cur = conn.cursor()
model = voyageai.Client()

def get_embedding(interest):
    return model.embed([interest], model = "voyage-3.5-lite", input_type="query").embeddings[0]


def search_documents(interest, limit=5):
    # Uses pgvector cosine similarity
    query_embedding = get_embedding(interest)
    cur.execute("""
        SELECT id, metadata, embedding <=> %s AS distance
        FROM documents
        ORDER BY distance
        LIMIT %s
    """, (query_embedding, limit))
    rows = cur.fetchall()
    return rows


def main(interests):
    clusters = {}
    for interest in interests:
        rows = search_documents(interest)
        for row in rows:
            id, metadata, distance = row

            if id in clusters:
                # add this distance to entry for cluster
                clusters[id][0].append(distance)
            else:
                clusters[id] = ([distance], metadata) 
    
    # sorting
    recommendations = []
    for id, (distances, metadata) in clusters.items():
        # Lower distance means higher similarity
        score = min(distances) / len(distances)
        recommendations.append((score, metadata))
    
    recommendations.sort(lambda x: x[0])
    # only return metadata
    return [metadata for score, metadata in recommendations]


def handler(payload):
    interests = payload.get(interests, '')
    print(f"Infer.py invoked with interests: {interests}")

    recommendations = main(interests)

    for i, metadata in enumerate(recommendations):
        print(f"------ CLUSTER {i} --------")
        print(metadata)

if __name__ == "__main__":
    interests = ["tariffs", "immigration", "foreign aid"]
    print(f"Infer.py invoked with interests: {interests}")

    recommendations = main(interests)

    for i, metadata in enumerate(recommendations):
        print(f"------ CLUSTER {i} --------")
        print(metadata)