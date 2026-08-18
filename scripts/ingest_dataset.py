import argparse
import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.rag.chunking.metadata import MetadataAwareChunkingStrategy
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.embedding_service import EmbeddingService

def ingest_dataset(
    language: str = "en",
    split: str = "train",
    limit: int = 100,
    chunk_strategy: str = "semantic",
    batch_size: int = 32,
    data_file: str = None
):
    print(f"Starting dataset ingestion pipeline (language={language}, limit={limit}, strategy={chunk_strategy})...")
    
    if not data_file:
        data_file = f"./data/msmarco_xi_{language}_{split}.json"

    if not os.path.exists(data_file):
        print(f"Data file '{data_file}' not found. Generating sample records...")
        records = [
            {
                "query_id": "q1",
                "passage_id": "p1",
                "passage": "New Delhi is the capital of India. It serves as the administrative center and houses parliament.",
                "language": language,
                "query_type": "factual"
            },
            {
                "query_id": "q2",
                "passage_id": "p2",
                "passage": "Retrieval Augmented Generation combines vector search with LLMs to eliminate hallucinations.",
                "language": language,
                "query_type": "technical"
            },
            {
                "query_id": "q3",
                "passage_id": "p3",
                "passage": "Qdrant stores document payloads alongside dense vectors for hybrid filtering and retrieval.",
                "language": language,
                "query_type": "technical"
            },
            {
                "query_id": "q4",
                "passage_id": "p4",
                "passage": "Sarvam AI Saaras v3 is engineered specifically for fast Indian language speech recognition.",
                "language": language,
                "query_type": "technical"
            }
        ]
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    subset = data[:limit]
    print(f"Loaded {len(subset)} passages from {data_file}.")

    # Initialize chunker & retrieval service
    embedding_service = EmbeddingService()
    chunker = MetadataAwareChunkingStrategy(
        strategy_name=chunk_strategy,
        embedding_service=embedding_service
    )
    retrieval_service = RetrievalService()

    all_chunks = []
    for idx, item in enumerate(subset):
        text = item.get("passage", item.get("text", ""))
        source_id = item.get("passage_id", f"doc_{idx}")
        q_id = item.get("query_id", "")
        q_type = item.get("query_type", "")
        lang = item.get("language", language)

        chunks = chunker.chunk_with_metadata(
            text=text,
            source_id=source_id,
            language=lang,
            query_id=q_id,
            query_type=q_type,
            passage_id=source_id
        )
        all_chunks.extend(chunks)

    print(f"Generated {len(all_chunks)} chunks from {len(subset)} passages.")

    # Index into Qdrant & BM25 in batches
    indexed_count = 0
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        count = retrieval_service.index_chunks(batch)
        indexed_count += count
        print(f"Indexed batch {i // batch_size + 1}: {count} chunks (Total: {indexed_count})")

    print(f"Ingestion complete! Total indexed chunks: {indexed_count}")
    return indexed_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest MSMARCO-XI dataset into Qdrant & BM25")
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--chunk-strategy", type=str, default="semantic", choices=["fixed", "sentence", "semantic"])
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--data-file", type=str, default=None)
    args = parser.parse_args()

    ingest_dataset(
        language=args.language,
        split=args.split,
        limit=args.limit,
        chunk_strategy=args.chunk_strategy,
        batch_size=args.batch_size,
        data_file=args.data_file
    )
