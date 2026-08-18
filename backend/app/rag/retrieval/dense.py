from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models

class QdrantDenseRetriever:
    """Dense vector retriever using Qdrant vector database."""
    def __init__(self, qdrant_client: QdrantClient, collection_name: str):
        self.client = qdrant_client
        self.collection_name = collection_name

    def search(
        self,
        query_vector: List[float],
        top_k: int = 20,
        filter_language: Optional[str] = None,
        filter_strategy: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        must_filters = []
        if filter_language:
            must_filters.append(
                models.FieldCondition(
                    key="language",
                    match=models.MatchValue(value=filter_language)
                )
            )
        if filter_strategy:
            must_filters.append(
                models.FieldCondition(
                    key="chunk_strategy",
                    match=models.MatchValue(value=filter_strategy)
                )
            )

        query_filter = models.Filter(must=must_filters) if must_filters else None

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True
            )
            hits = []
            for point in results:
                payload = point.payload or {}
                hits.append({
                    "chunk_id": payload.get("chunk_id", str(point.id)),
                    "text": payload.get("text", ""),
                    "score": float(point.score),
                    "source_id": payload.get("source_id", ""),
                    "passage_id": payload.get("passage_id", ""),
                    "query_id": payload.get("query_id", ""),
                    "language": payload.get("language", "en"),
                    "chunk_strategy": payload.get("chunk_strategy", "semantic"),
                    "payload": payload
                })
            return hits
        except Exception as e:
            # Return empty list on connection/search failure gracefully
            return []
