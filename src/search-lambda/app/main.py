from fastapi import FastAPI
from pymongo import MongoClient
import hdbscan
import numpy as np
from datetime import datetime
from collections import defaultdict

app = FastAPI()

# MongoDB Atlas client
# 👉 Set MONGODB_URI in AWS Lambda environment variables
client = MongoClient("DB_URI")
db = client["auxiom_database"]
events = db["events"]

@app.get("/search")
async def search(query: str, top_k: int = 50, min_cluster_size: int = 2):
    # Step 1: Query Atlas Search
    pipeline = [
        {"$search": {"index": "tags", "text": {"query": query, "path": ["title", "body"]}}},
        {"$limit": top_k}
    ]
    results = list(events.aggregate(pipeline))

    if not results:
        return {"clusters": []}

    # Step 2: Extract embeddings
    embeddings = np.array([r["embedding"] for r in results])

    # Step 3: Cluster
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    labels = clusterer.fit_predict(embeddings)

    # Step 4: Group & sort
    clusters = defaultdict(list)
    for label, item in zip(labels, results):
        if label == -1:  # HDBSCAN noise
            continue
        clusters[label].append(item)

    # TODO: Segregate by implemented vs pending
    for label in clusters:
        clusters[label].sort(key=lambda x: datetime.fromisoformat(x["bill"]["date"]))

    # Drop unnecessary fields
    for label in clusters:
        for item in clusters[label]:
            del item["embedding"]

    return {
        "clusters": [
            {"cluster_id": int(label), "items": clusters[label]}
            for label in clusters
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)