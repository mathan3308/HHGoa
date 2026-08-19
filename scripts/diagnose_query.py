"""
Step-by-Step RAG Query Pipeline Diagnostic CLI
Usage: python scripts/diagnose_query.py --query "YOUR QUESTION HERE"
Traces execution across Query -> Embedding -> Dense Hits -> Sparse Hits -> RRF -> Relevance -> LLM -> Grounding
"""

import argparse
import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.rag.pipeline import VoiceRAGPipeline
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.guardrails.relevance_guard import RelevanceGuard
from backend.app.services.generation_service import GenerationService
from backend.app.guardrails.grounding_guard import GroundingGuard
from backend.app.config import settings

async def diagnose_query(query: str):
    print("============================================================")
    print(f"RAG PIPELINE DIAGNOSTIC TRACE FOR QUERY: '{query}'")
    print("============================================================")

    # 1. Query Normalization & Language Check
    clean_query = query.strip()
    print(f"\n[1] NORMALIZED QUERY: '{clean_query}'")

    # 2. Embedding Info
    emb_service = EmbeddingService()
    emb_vec = emb_service.embed_query(clean_query)
    print(f"[2] EMBEDDING MODEL: '{settings.EMBEDDING_MODEL}'")
    print(f"    Vector Dimension: {len(emb_vec)} | Sample (first 5): {[round(x, 4) for x in emb_vec[:5]]}")

    # 3. Dense Retrieval
    ret_service = RetrievalService()
    dense_hits = []
    if ret_service.dense_retriever:
        dense_hits = ret_service.dense_retriever.search(emb_vec, top_k=5)
    print(f"\n[3] DENSE RETRIEVAL HITS ({len(dense_hits)}):")
    for idx, hit in enumerate(dense_hits, start=1):
        print(f"    #{idx} Score: {hit.get('score', 0):.4f} | ID: {hit.get('source_id')} | Text: '{hit.get('text', '')[:80]}...'")

    # 4. Sparse BM25 Retrieval
    sparse_hits = ret_service.sparse_retriever.search(clean_query, top_k=5)
    print(f"\n[4] SPARSE (BM25) RETRIEVAL HITS ({len(sparse_hits)}):")
    for idx, hit in enumerate(sparse_hits, start=1):
        print(f"    #{idx} Score: {hit.get('bm25_score', 0):.4f} | ID: {hit.get('source_id')} | Text: '{hit.get('text', '')[:80]}...'")

    # 5. Hybrid RRF Retrieval
    fused = ret_service.hybrid_retrieve(clean_query, top_k=settings.TOP_K)
    print(f"\n[5] HYBRID RRF FUSED TOP RESULTS ({len(fused)}):")
    for idx, hit in enumerate(fused, start=1):
        print(f"    #{idx} RRF Score: {hit.get('relevance_score', 0):.4f} | ID: {hit.get('source_id')} | Text: '{hit.get('text', '')[:80]}...'")

    # 6. Relevance Guard Decision
    rel_guard = RelevanceGuard(threshold=settings.RETRIEVAL_THRESHOLD)
    has_context, rel_reason = rel_guard.validate(fused)
    print(f"\n[6] RELEVANCE GUARD DECISION: {has_context} ({rel_reason})")

    # 7. LLM Answer Generation
    gen_service = GenerationService()
    print(f"\n[7] LLM GENERATION MODEL: '{settings.SARVAM_LLM_MODEL}'")
    answer = await gen_service.generate(clean_query, fused)
    print(f"    Generated Answer: '{answer}'")

    # 8. Grounding Validation Decision
    g_guard = GroundingGuard(threshold=settings.GROUNDING_THRESHOLD)
    g_res = g_guard.validate(answer, fused)
    print(f"\n[8] GROUNDING VALIDATION DECISION:")
    print(f"    Grounded: {g_res.grounded} | Reason: '{g_res.reason}' | Confidence: {g_res.confidence}")

    print("\n============================================================")
    print("DIAGNOSTIC TRACE COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step-by-step diagnostic CLI for RAG pipeline")
    parser.add_argument("--query", type=str, default="How does photosynthesis help plants survive?")
    args = parser.parse_args()

    asyncio.run(diagnose_query(args.query))
