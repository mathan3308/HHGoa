"""
Official AI4Bharat/MSMARCO-XI Scalable Dataset Ingestion Engine
Streams dataset from Hugging Face, chunks passages, embeds in batches, upserts to Qdrant (msmarco_xi_full),
and maintains a resumable state checkpoint.

Modes:
- sample: Ingest limited development subset (e.g., --limit 20)
- language: Ingest specific language configurations (e.g., --languages ta,hi)
- full: Ingest all available language records from train/validation splits
"""

import argparse
import csv
import json
import os
import sys
import time
import uuid
from typing import Dict, List, Any, Optional

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datasets import load_dataset
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.rag.chunking.metadata import MetadataAwareChunkingStrategy
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.retrieval_service import RetrievalService

STATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "ingestion_state"))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
CHECKPOINT_FILE = os.path.join(STATE_DIR, "checkpoint.json")

def load_checkpoint() -> Dict[str, Any]:
    os.makedirs(STATE_DIR, exist_ok=True)
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return {
        "completed_splits": [],
        "records_processed": 0,
        "passages_processed": 0,
        "chunks_generated": 0,
        "embeddings_generated": 0,
        "qdrant_points_inserted": 0,
        "language_stats": {}
    }

def save_checkpoint(state: Dict[str, Any]) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def extract_record_passages(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts valid selected passages from official MSMARCO-XI record schema."""
    extracted = []
    source_lang = item.get("source_lang", "en")
    target_lang = item.get("target_lang", "en")
    query_id = str(item.get("query_id", ""))
    query_type = item.get("query_type", "general")
    query = item.get("query", item.get("Eng_Query", ""))
    answer = item.get("Answer", item.get("Eng_Answer", ""))

    passages_dict = item.get("passages", {})
    if isinstance(passages_dict, dict):
        eng_passages = passages_dict.get("English_passages", []) or []
        trans_passages = passages_dict.get("Translated_passages", []) or []
        is_selected_list = passages_dict.get("is_selected", []) or []

        # Iterate over passages and keep selected ones (is_selected == 1)
        for idx in range(max(len(eng_passages), len(trans_passages))):
            sel = is_selected_list[idx] if idx < len(is_selected_list) else 1
            if sel != 1 and len(is_selected_list) > 0:
                continue

            text_content = ""
            if idx < len(trans_passages) and trans_passages[idx]:
                text_content = trans_passages[idx].strip()
            elif idx < len(eng_passages) and eng_passages[idx]:
                text_content = eng_passages[idx].strip()

            if not text_content:
                continue

            extracted.append({
                "text": text_content,
                "language": target_lang if target_lang else "en",
                "source_lang": source_lang,
                "target_lang": target_lang,
                "query_id": query_id,
                "query_type": query_type,
                "query": query,
                "answer": answer,
                "passage_index": idx + 1,
                "is_selected": sel,
                "source_dataset": "ai4bharat/MSMARCO-XI"
            })

    # Fallback if item is plain text record
    if not extracted and ("passage" in item or "text" in item):
        txt = item.get("passage", item.get("text", "")).strip()
        if txt:
            extracted.append({
                "text": txt,
                "language": item.get("language", target_lang),
                "source_lang": source_lang,
                "target_lang": target_lang,
                "query_id": query_id,
                "query_type": query_type,
                "query": query,
                "answer": answer,
                "passage_index": 1,
                "is_selected": 1,
                "source_dataset": "ai4bharat/MSMARCO-XI"
            })

    return extracted

def ingest_official_dataset(
    languages: str = "all",
    splits: str = "train,validation",
    limit: Optional[int] = None,
    chunk_strategy: str = "semantic",
    embedding_batch_size: int = 64,
    qdrant_batch_size: int = 256,
    ingest_mode: str = "sample"
):
    print("============================================================")
    print(f"STARTING OFFICIAL MSMARCO-XI DATASET INGESTION ({ingest_mode.upper()} MODE)")
    print("============================================================")
    print(f"Dataset: {settings.DATASET_NAME} | Config: {settings.DATASET_CONFIG}")
    print(f"Target Collection: {settings.QDRANT_COLLECTION_NAME}")
    print(f"Mode: {ingest_mode} | Limit: {limit or 'No Limit'} | Chunk Strategy: {chunk_strategy}")

    os.makedirs(REPORTS_DIR, exist_ok=True)
    state = load_checkpoint()
    
    embedding_service = EmbeddingService()
    chunker = MetadataAwareChunkingStrategy(strategy_name=chunk_strategy, embedding_service=embedding_service)
    retrieval_service = RetrievalService()

    split_list = [s.strip() for s in splits.split(",") if s.strip()]
    target_langs = [l.strip() for l in languages.split(",") if l.strip()]

    start_time = time.time()
    
    for split in split_list:
        split_key = f"{settings.DATASET_CONFIG}_{split}"
        if split_key in state["completed_splits"] and not limit:
            print(f"Split '{split_key}' already completed in previous run. Skipping.")
            continue

        print(f"\n--- Processing Dataset Split: '{split}' ---")
        try:
            ds = load_dataset(settings.DATASET_NAME, settings.DATASET_CONFIG, split=split, streaming=True)
        except Exception as e:
            print(f"Note: Remote HuggingFace stream failed: {e}. Falling back to local data file...")
            local_file = "./data/msmarco_xi_en_train.json"
            if not os.path.exists(local_file):
                print("Error: Local dataset file not found.")
                return 0
            with open(local_file, "r", encoding="utf-8") as f:
                ds = json.load(f)

        chunk_buffer = []
        record_counter = 0

        for item in ds:
            # Check language filter
            item_lang = item.get("target_lang", item.get("language", "en"))
            if "all" not in target_langs and item_lang not in target_langs:
                continue

            record_counter += 1
            state["records_processed"] += 1

            passages = extract_record_passages(item)
            state["passages_processed"] += len(passages)

            for p_idx, p in enumerate(passages):
                chunks = chunker.chunk_with_metadata(
                    text=p["text"],
                    source_id=f"p_{p['query_id']}_{p['passage_index']}",
                    language=p["language"],
                    query_id=p["query_id"],
                    query_type=p["query_type"],
                    passage_id=f"p_{p['query_id']}_{p['passage_index']}"
                )

                for c in chunks:
                    c["source_lang"] = p["source_lang"]
                    c["target_lang"] = p["target_lang"]
                    c["split"] = split
                    c["is_selected"] = p["is_selected"]
                    c["source_dataset"] = settings.DATASET_NAME
                    chunk_buffer.append(c)
                    state["chunks_generated"] += 1

            # Ingest batch when chunk_buffer reaches qdrant_batch_size
            if len(chunk_buffer) >= qdrant_batch_size:
                count = retrieval_service.index_chunks(chunk_buffer)
                state["embeddings_generated"] += count
                state["qdrant_points_inserted"] += count
                
                lang_key = item_lang
                state["language_stats"][lang_key] = state["language_stats"].get(lang_key, 0) + count
                chunk_buffer = []

                if state["qdrant_points_inserted"] % 100 == 0 or record_counter % 50 == 0:
                    save_checkpoint(state)
                    print(f"Ingested {state['qdrant_points_inserted']} points across {state['records_processed']} records...")

            if limit and record_counter >= limit:
                print(f"Reached record limit ({limit}) for split '{split}'.")
                break

        # Flush remaining chunk buffer
        if chunk_buffer:
            count = retrieval_service.index_chunks(chunk_buffer)
            state["embeddings_generated"] += count
            state["qdrant_points_inserted"] += count
            chunk_buffer = []

        if not limit:
            state["completed_splits"].append(split_key)
        save_checkpoint(state)

    end_time = time.time()

    # Generate Manifest Report
    manifest = {
        "dataset": settings.DATASET_NAME,
        "config": settings.DATASET_CONFIG,
        "ingest_mode": ingest_mode,
        "languages": target_langs,
        "splits": split_list,
        "records_processed": state["records_processed"],
        "passages_processed": state["passages_processed"],
        "chunks_generated": state["chunks_generated"],
        "embeddings_generated": state["embeddings_generated"],
        "qdrant_points_inserted": state["qdrant_points_inserted"],
        "duration_seconds": round(end_time - start_time, 2),
        "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    manifest_file = os.path.join(REPORTS_DIR, "dataset_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Generate Per-Language CSV Report
    csv_file = os.path.join(REPORTS_DIR, "dataset_language_report.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "indexed_points"])
        for l_code, p_count in state["language_stats"].items():
            writer.writerow([l_code, p_count])

    print("\n============================================================")
    print(f"INGESTION COMPLETE! Total Qdrant Points Inserted: {state['qdrant_points_inserted']}")
    print(f"Saved manifest to '{manifest_file}' and language report to '{csv_file}'")
    print("============================================================")
    return state["qdrant_points_inserted"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest official AI4Bharat/MSMARCO-XI dataset into Qdrant msmarco_xi_full")
    parser.add_argument("--languages", type=str, default="all")
    parser.add_argument("--splits", type=str, default="train,validation")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--chunk-strategy", type=str, default="semantic")
    parser.add_argument("--ingest-mode", type=str, default="sample", choices=["sample", "language", "full"])
    args = parser.parse_args()

    ingest_official_dataset(
        languages=args.languages,
        splits=args.splits,
        limit=args.limit,
        chunk_strategy=args.chunk_strategy,
        ingest_mode=args.ingest_mode
    )
