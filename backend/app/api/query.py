import uuid
from fastapi import APIRouter, HTTPException, Header
from backend.app.models.request_models import TextQueryRequest
from backend.app.models.response_models import VoiceQueryResponse
from backend.app.rag.pipeline import VoiceRAGPipeline

router = APIRouter(prefix="/api", tags=["Query"])
pipeline = VoiceRAGPipeline()

@router.post("/query", response_model=VoiceQueryResponse)
async def text_query(
    request: TextQueryRequest,
    x_request_id: str = Header(default=None)
):
    req_id = x_request_id or str(uuid.uuid4())
    try:
        response = await pipeline.process_text_query(
            query=request.query,
            language=request.language or "en",
            request_id=req_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text query pipeline failure: {str(e)}")
