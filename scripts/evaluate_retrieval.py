import argparse
import os
import sys
import time
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.rag.chunking.fixed import FixedChunkingStrategy
from backend.app.rag.chunking.sentence import SentenceChunkingStrategy
from backend.app.rag.chunking.semantic import SemanticChunkingStrategy
from backend.app.rag.chunking.metadata import MetadataAwareChunkingStrategy
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.retrieval_service import RetrievalService

# Multi-paragraph evaluation corpus representing rich MSMARCO-XI passages
EVALUATION_PASSAGES = [
    {
        "id": "p1",
        "query": "What is the capital of India and its government setup?",
        "text": """New Delhi is the capital of India and an administrative district within the National Capital Territory of Delhi. New Delhi houses all three branches of the Government of India, including the Rashtrapati Bhavan, Parliament House, and the Supreme Court of India. The city was originally laid out by British architects Sir Edwin Lutyens and Sir Herbert Baker during the early twentieth century.

The city plays a vital role as the political and financial core of Northern India. It accommodates major foreign embassies, international organizations, and corporate headquarters. Public transportation in New Delhi relies heavily on the Delhi Metro network, which connects the capital to satellite cities such as Gurgaon, Noida, and Faridabad. The culture of New Delhi is cosmopolitan, reflecting diverse traditions, cuisines, and languages from all across India."""
    },
    {
        "id": "p2",
        "query": "How does Retrieval Augmented Generation combine vector databases with language models?",
        "text": """Retrieval-Augmented Generation (RAG) is an advanced architectural pattern designed to enhance the accuracy and reliability of Large Language Models (LLMs) by grounding them on external knowledge bases. Instead of relying solely on parametric memory learned during pre-training, RAG dynamically retrieves relevant context passages from a vector database prior to generating an answer.

In a standard RAG pipeline, input documents are first normalized, split into optimal chunks using specific chunking strategies, and converted into dense vector representations using multilingual embedding models. These vector embeddings are stored in high-performance vector search engines like Qdrant using index structures such as HNSW.

When a user submits a question, the query is embedded into the same vector space to perform nearest neighbor search alongside sparse keyword algorithms like BM25. Reciprocal Rank Fusion (RRF) then merges the dense and sparse candidate lists into a final top-k context. This context is injected into a strict system prompt provided to the LLM, effectively eliminating hallucinations and ensuring responses are verifiably grounded in retrieved facts."""
    },
    {
        "id": "p3",
        "query": "What is Sarvam AI Saaras v3 speech to text capabilities?",
        "text": """Sarvam AI's Saaras v3 represents a state-of-the-art speech-to-text model engineered specifically for Indian languages, accents, and code-mixed speech scenarios. Trained on thousands of hours of high-quality audio data across regional languages such as Hindi, Tamil, Telugu, Kannada, Bengali, and English, Saaras v3 delivers exceptional transcription accuracy even in noisy acoustic environments.

The API processes incoming audio streams or uploaded audio files with minimal latency, returning structured JSON output containing the recognized transcript, language code, confidence metrics, and duration. By integrating Saaras v3 into voice-enabled AI pipelines, developers can build conversational interfaces that understand diverse Indian accents seamlessly."""
    },
    {
        "id": "p4",
        "query": "How does Qdrant vector database handle payload filtering and hybrid search?",
        "text": """Qdrant is an open-source vector search engine built in Rust that provides fast vector similarity search alongside rich payload filtering capabilities. Unlike traditional vector databases that separate metadata filtering from vector search, Qdrant executes filtering directly during vector index traversal, preserving high recall even under strict metadata constraints.

Qdrant supports multiple distance metrics including Cosine, Euclidean, and Dot Product distances. It utilizes the Hierarchical Navigable Small World (HNSW) graph algorithm for fast approximate nearest neighbor (ANN) retrieval. Furthermore, Qdrant allows developers to attach arbitrary JSON payloads to vector points, facilitating multi-tenant isolation, language filtering, and hybrid RRF search integration."""
    }
]

def evaluate_chunking_and_retrieval():
    print("==================================================")
    print("EMPIRICAL CHUNKING & RETRIEVAL EVALUATION AUDIT")
    print("==================================================\n")

    embedding_service = EmbeddingService()
    strategies = ["fixed", "sentence", "semantic", "metadata-aware"]
    eval_reports = []

    for strat in strategies:
        print(f"--> Auditing Strategy: '{strat.upper()}'...")
        chunker = MetadataAwareChunkingStrategy(strategy_name=strat, embedding_service=embedding_service)

        start_time = time.perf_counter()
        all_chunks = []
        for passage_item in EVALUATION_PASSAGES:
            chunks = chunker.chunk_with_metadata(
                text=passage_item["text"],
                source_id=passage_item["id"],
                language="en",
                passage_id=passage_item["id"]
            )
            all_chunks.extend(chunks)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        num_chunks = len(all_chunks)
        chunk_word_counts = [len(c["text"].split()) for c in all_chunks]
        min_words = min(chunk_word_counts) if chunk_word_counts else 0
        max_words = max(chunk_word_counts) if chunk_word_counts else 0
        avg_words = sum(chunk_word_counts) / num_chunks if num_chunks > 0 else 0

        # Run empirical retrieval test against evaluating queries
        retrieval_service = RetrievalService()
        retrieval_service.index_chunks(all_chunks)

        recalls_at_1 = []
        recalls_at_5 = []
        mrr_list = []

        for p_item in EVALUATION_PASSAGES:
            query = p_item["query"]
            target_source = p_item["id"]
            hits = retrieval_service.hybrid_retrieve(query=query, top_k=5)

            retrieved_sources = [h.get("source_id", h.get("passage_id")) for h in hits]
            
            # Recall@1
            r1 = 1.0 if (len(retrieved_sources) > 0 and retrieved_sources[0] == target_source) else 0.0
            recalls_at_1.append(r1)

            # Recall@5
            r5 = 1.0 if target_source in retrieved_sources[:5] else 0.0
            recalls_at_5.append(r5)

            # MRR
            mrr = 0.0
            if target_source in retrieved_sources:
                rank = retrieved_sources.index(target_source) + 1
                mrr = 1.0 / rank
            mrr_list.append(mrr)

        avg_r1 = sum(recalls_at_1) / len(recalls_at_1)
        avg_r5 = sum(recalls_at_5) / len(recalls_at_5)
        avg_mrr = sum(mrr_list) / len(mrr_list)

        report_entry = {
            "strategy": strat,
            "source_records": len(EVALUATION_PASSAGES),
            "num_chunks": num_chunks,
            "min_words": min_words,
            "max_words": max_words,
            "avg_words": round(avg_words, 1),
            "processing_ms": round(latency_ms, 2),
            "recall_at_1": round(avg_r1, 2),
            "recall_at_5": round(avg_r5, 2),
            "mrr": round(avg_mrr, 2),
            "sample_previews": [c["text"][:80] + "..." for c in all_chunks[:3]]
        }
        eval_reports.append(report_entry)

    # Print Detailed Statistics Table
    print("\n" + "=" * 90)
    print(f"{'Strategy':<15} | {'Chunks':<7} | {'Min W':<6} | {'Max W':<6} | {'Avg W':<7} | {'Recall@1':<9} | {'Recall@5':<9} | {'MRR':<6}")
    print("-" * 90)
    for r in eval_reports:
        print(f"{r['strategy']:<15} | {r['num_chunks']:<7} | {r['min_words']:<6} | {r['max_words']:<6} | {r['avg_words']:<7.1f} | {r['recall_at_1']:<9.2f} | {r['recall_at_5']:<9.2f} | {r['mrr']:<6.2f}")
    print("=" * 90 + "\n")

    print("SAMPLE CHUNK PREVIEWS:")
    for r in eval_reports:
        print(f"\n[{r['strategy'].upper()}] (Avg {r['avg_words']} words/chunk):")
        for i, prev in enumerate(r['sample_previews'], start=1):
            print(f"  Chunk {i}: \"{prev}\"")
    print("\n==================================================\n")

    return eval_reports

if __name__ == "__main__":
    evaluate_chunking_and_retrieval()
