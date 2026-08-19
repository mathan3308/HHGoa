from datetime import datetime
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.models.response_models import HealthCheckResponse
from backend.app.services.retrieval_service import RetrievalService

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
@router.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    retrieval_service = RetrievalService()
    qdrant_status = "ok" if retrieval_service.client else "disconnected"

    q_points = len(retrieval_service.indexed_docs)
    if retrieval_service.client:
        try:
            res = retrieval_service.client.count(collection_name=settings.QDRANT_COLLECTION_NAME)
            q_points = res.count
        except Exception:
            pass

    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "api": "ok",
            "qdrant": qdrant_status,
            "embedding": "ok",
            "stt": "mock" if settings.MOCK_EXTERNAL_SERVICES or not settings.SARVAM_API_KEY else "sarvam",
            "llm": "mock" if settings.MOCK_EXTERNAL_SERVICES or not settings.SARVAM_API_KEY else "sarvam"
        },
        mock_mode=settings.MOCK_EXTERNAL_SERVICES,
        dataset=settings.DATASET_NAME,
        collection=settings.QDRANT_COLLECTION_NAME,
        index_mode=settings.INGEST_MODE,
        languages=settings.DATASET_LANGUAGES,
        qdrant_points=q_points,
        embedding_model=settings.EMBEDDING_MODEL
    )
