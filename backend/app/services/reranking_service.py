from typing import List, Dict, Any
from backend.app.config import settings

class RerankingService:
    """
    Optional reranking module.
    Controlled by USE_RERANKER environment variable.
    Default path is latency-aware (USE_RERANKER=false).
    """
    def __init__(self, enabled: bool = None):
        self.enabled = enabled if enabled is not None else settings.USE_RERANKER

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not candidates or not self.enabled:
            return candidates[:top_k]

        # Fast keyword-overlap reranker for lightweight sub-ms reranking
        query_words = set(query.lower().split())
        for doc in candidates:
            doc_words = set(doc.get("text", "").lower().split())
            overlap = len(query_words.intersection(doc_words))
            base_score = doc.get("relevance_score", doc.get("score", 0.5))
            doc["relevance_score"] = float(round(base_score + 0.05 * overlap, 4))

        reranked = sorted(candidates, key=lambda x: x["relevance_score"], reverse=True)
        return reranked[:top_k]
