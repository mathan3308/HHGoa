import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.app.models.request_models import SearchRequest
from backend.app.models.response_models import SearchResponse, SearchResultItem
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/api", tags=["Search & Metrics"])
retrieval_service = RetrievalService()
benchmark_service = BenchmarkService()

@router.post("/search", response_model=SearchResponse)
async def search_index(request: SearchRequest):
    start = time.perf_counter()
    try:
        results = retrieval_service.hybrid_retrieve(
            query=request.query,
            top_k=request.top_k or 10,
            filter_strategy=request.chunk_strategy
        )
        latency_ms = round((time.perf_counter() - start) * 1000.0, 2)

        items = [
            SearchResultItem(
                chunk_id=r.get("chunk_id", f"item_{idx}"),
                text=r.get("text", ""),
                score=float(r.get("relevance_score", r.get("score", 0.0))),
                metadata=r
            ) for idx, r in enumerate(results)
        ]

        return SearchResponse(query=request.query, results=items, latency_ms=latency_ms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    return benchmark_service.get_summary()
