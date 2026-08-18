import argparse
import asyncio
import csv
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.rag.pipeline import VoiceRAGPipeline
from backend.app.services.retrieval_service import RetrievalService

BENCHMARK_QUERIES = [
    "What is the capital of India?",
    "How does Retrieval Augmented Generation work in LLM pipelines?",
    "What vector database does Qdrant use under the hood?",
    "What is Sarvam AI saaras v3 model used for?",
    "Explain the Reciprocal Rank Fusion algorithm in hybrid search.",
    "What languages does the MSMARCO Indian language dataset support?",
    "How to prevent hallucinated answers in Voice RAG models?",
    "What is the recommended chunk size for semantic sentence splitting?",
    "Explain the difference between dense semantic retrieval and sparse BM25 search.",
    "How does the input guardrail detect prompt injection attempts?",
]

async def run_benchmark(num_queries: int = 50, strategy: str = "semantic"):
    print(f"==================================================")
    print(f"Starting Voice RAG Latency Benchmark ({num_queries} queries, strategy={strategy})")
    print(f"==================================================")

    pipeline = VoiceRAGPipeline()
    retrieval_service = RetrievalService()

    # Ensure index has data for benchmarking
    if not retrieval_service.indexed_docs:
        print("Pre-loading benchmark sample passages into index...")
        from scripts.ingest_dataset import ingest_dataset
        ingest_dataset(limit=50, chunk_strategy=strategy)

    records = []
    
    for i in range(num_queries):
        query = BENCHMARK_QUERIES[i % len(BENCHMARK_QUERIES)]
        query_text = f"{query} (Iteration {i+1})"
        
        start_time = time.perf_counter()
        response = await pipeline.process_text_query(query=query_text)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        rec = {
            "query_index": i + 1,
            "query": query,
            "strategy": strategy,
            "stt_ms": response.latency.stt_ms,
            "embedding_ms": response.latency.embedding_ms,
            "retrieval_ms": response.latency.retrieval_ms,
            "reranking_ms": response.latency.reranking_ms,
            "generation_ms": response.latency.generation_ms,
            "guardrail_ms": response.latency.guardrail_ms,
            "total_rag_ms": response.latency.total_rag_ms,
            "total_end_to_end_ms": response.latency.total_end_to_end_ms,
            "grounded": response.grounded,
            "status": response.status
        }
        records.append(rec)
        print(f"[{i+1}/{num_queries}] RAG Latency: {rec['total_rag_ms']:.2f}ms | Grounded: {rec['grounded']}")

    # Calculate P50, P70, P100, min, max, mean for total_rag_ms and total_end_to_end_ms
    rag_latencies = [r["total_rag_ms"] for r in records]
    e2e_latencies = [r["total_end_to_end_ms"] for r in records]
    emb_latencies = [r["embedding_ms"] for r in records]
    ret_latencies = [r["retrieval_ms"] for r in records]
    gen_latencies = [r["generation_ms"] for r in records]

    results_summary = {
        "benchmark_metadata": {
            "num_queries": num_queries,
            "strategy": strategy,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "total_rag_ms": {
                "p50": float(np.percentile(rag_latencies, 50)),
                "p70": float(np.percentile(rag_latencies, 70)),
                "p100": float(np.max(rag_latencies)),
                "mean": float(np.mean(rag_latencies)),
                "min": float(np.min(rag_latencies)),
                "max": float(np.max(rag_latencies))
            },
            "end_to_end_ms": {
                "p50": float(np.percentile(e2e_latencies, 50)),
                "p70": float(np.percentile(e2e_latencies, 70)),
                "p100": float(np.max(e2e_latencies)),
                "mean": float(np.mean(e2e_latencies)),
                "min": float(np.min(e2e_latencies)),
                "max": float(np.max(e2e_latencies))
            },
            "embedding_ms_mean": float(np.mean(emb_latencies)),
            "retrieval_ms_mean": float(np.mean(ret_latencies)),
            "generation_ms_mean": float(np.mean(gen_latencies))
        }
    }

    # Save benchmark_results.json
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    # Save benchmark_report.csv
    with open("benchmark_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print("\n==================================================")
    print("BENCHMARK COMPLETED SUCCESSFULLY!")
    print(f"Total Queries Executed: {num_queries}")
    print(f"RAG Latency P50 : {results_summary['metrics']['total_rag_ms']['p50']:.2f} ms")
    print(f"RAG Latency P70 : {results_summary['metrics']['total_rag_ms']['p70']:.2f} ms")
    print(f"RAG Latency P100: {results_summary['metrics']['total_rag_ms']['p100']:.2f} ms")
    print(f"Mean RAG Latency: {results_summary['metrics']['total_rag_ms']['mean']:.2f} ms")
    print("Saved benchmark_results.json and benchmark_report.csv")
    print("==================================================\n")

    return results_summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG latency benchmark suite")
    parser.add_argument("--num-queries", type=int, default=50)
    parser.add_argument("--strategy", type=str, default="semantic")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.num_queries, args.strategy))
