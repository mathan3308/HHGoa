import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.app.config import settings

def build_index(recreate: bool = False, vector_size: int = 384):
    print(f"Connecting to Qdrant at {settings.QDRANT_URL}...")
    try:
        if settings.QDRANT_API_KEY:
            client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        else:
            client = QdrantClient(url=settings.QDRANT_URL)
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        return False

    collection_name = settings.QDRANT_COLLECTION_NAME
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)

    if exists and recreate:
        print(f"Recreating Qdrant collection '{collection_name}' (--recreate flag passed)...")
        client.delete_collection(collection_name=collection_name)
        exists = False

    if not exists:
        print(f"Creating collection '{collection_name}' (vector_size={vector_size}, distance=COSINE)...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print("Collection created successfully.")
    else:
        print(f"Collection '{collection_name}' already exists.")

    info = client.get_collection(collection_name=collection_name)
    print(f"Qdrant Index Statistics for '{collection_name}':")
    print(f"- Vectors Count: {info.vectors_count}")
    print(f"- Points Count: {info.points_count}")
    print(f"- Status: {info.status}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize and verify Qdrant Vector Collection")
    parser.add_argument("--recreate", action="store_true", help="Recreate collection if it already exists")
    parser.add_argument("--vector-size", type=int, default=384, help="Embedding vector dimension size")
    args = parser.parse_args()

    build_index(recreate=args.recreate, vector_size=args.vector_size)
