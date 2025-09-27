from fastapi import FastAPI
from pymongo import MongoClient
import hdbscan
import numpy as np
from datetime import datetime
from collections import defaultdict
from mangum import Mangum
import os
from pymongo.server_api import ServerApi

app = FastAPI()

# MongoDB Atlas client
# 👉 Set MONGODB_URI in AWS Lambda environment variables
uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["auxiom_database"]
events = db["events"]

@app.get("/search")
async def search(query: str, top_k: int = 50, min_cluster_size: int = 2):
    # Step 1: Query Atlas Search
    print(f"Search endpoint invoked with {query}")
    pipeline = [
        {"$search": {"index": "tags", "text": {"query": query, "path": ["tags", "topics"]}}},
        {"$limit": top_k}
    ]
    results = list(events.aggregate(pipeline))

    if not results:
        return {"clusters": []}

    print(f"Found {len(results)} results")
    # Step 2: Extract embeddings
    embeddings = np.array([r["embedding"] for r in results])

    # Step 3: Cluster
    print("Clustering...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    print("Fitting...")
    labels = clusterer.fit_predict(embeddings)
    print("Done clustering!")
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
            del item["_id"]


    ans = {
        "clusters": [
            {"cluster_id": int(label), "items": clusters[label]}
            for label in clusters
        ]
    }

    return ans

handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)