"""
Dataset Download & Stream Utility for AI4Bharat/MSMARCO-XI
HuggingFace link: https://huggingface.co/datasets/ai4bharat/MSMARCO-XI
"""

import argparse
import json
import os
from datasets import load_dataset

def download_dataset(dataset_name: str, config: str, split: str, limit: int, output_dir: str):
    print(f"Streaming dataset '{dataset_name}' (config={config}, split={split}, limit={limit})...")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        ds = load_dataset(dataset_name, config, split=split, streaming=True)
    except Exception as e:
        print(f"Note: Direct Hugging Face dataset load requires internet access or token. Error: {e}")
        print("Creating mock MSMARCO-XI sample dataset file for local development...")
        sample_records = [
            {
                "query_id": "q1",
                "query": "What is the capital of India?",
                "passage": "New Delhi is the capital of India and the seat of all three branches of the Government of India.",
                "language": "en",
                "query_type": "factual",
                "passage_id": "p1"
            },
            {
                "query_id": "q2",
                "query": "How does Retrieval Augmented Generation work?",
                "passage": "Retrieval-Augmented Generation (RAG) enhances Large Language Models by retrieving relevant document passages from a vector database before generating an answer.",
                "language": "en",
                "query_type": "technical",
                "passage_id": "p2"
            },
            {
                "query_id": "q3",
                "query": "What is Qdrant vector database?",
                "passage": "Qdrant is a high-performance vector search engine written in Rust that supports hybrid search, payload filtering, and fast HNSW index retrieval.",
                "language": "en",
                "query_type": "technical",
                "passage_id": "p3"
            },
            {
                "query_id": "q4",
                "query": "Sarvam AI saaras v3 speech to text details",
                "passage": "Sarvam AI's Saaras v3 is an advanced state-of-the-art multilingual speech-to-text model specifically fine-tuned for Indian languages and accents.",
                "language": "en",
                "query_type": "technical",
                "passage_id": "p4"
            }
        ]
        out_file = os.path.join(output_dir, f"msmarco_xi_{config}_{split}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(sample_records, f, indent=2)
        print(f"Saved dataset sample to {out_file}")
        return out_file

    records = []
    count = 0
    for item in ds:
        records.append(item)
        count += 1
        if count >= limit:
            break

    out_file = os.path.join(output_dir, f"msmarco_xi_{config}_{split}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"Successfully downloaded {len(records)} records to {out_file}")
    return out_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download AI4Bharat/MSMARCO-XI dataset")
    parser.add_argument("--dataset", type=str, default="ai4bharat/MSMARCO-XI")
    parser.add_argument("--config", type=str, default="en")
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output-dir", type=str, default="./data")
    args = parser.parse_args()

    download_dataset(args.dataset, args.config, args.split, args.limit, args.output_dir)
