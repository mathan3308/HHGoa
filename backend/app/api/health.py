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
        mock_mode=settings.MOCK_EXTERNAL_SERVICES
    )
