import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Header
from backend.app.core.security import validate_audio_file
from backend.app.models.response_models import VoiceQueryResponse, TranscriptResponse
from backend.app.rag.pipeline import VoiceRAGPipeline
from backend.app.services.speech_service import SpeechService

router = APIRouter(prefix="/api", tags=["Voice"])
pipeline = VoiceRAGPipeline()
speech_service = SpeechService()

@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    contents = await file.read()
    validate_audio_file(file, contents)
    try:
        return await speech_service.transcribe_audio(contents, file.filename or "audio.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    file: UploadFile = File(...),
    x_request_id: str = Header(default=None)
):
    contents = await file.read()
    validate_audio_file(file, contents)
    req_id = x_request_id or str(uuid.uuid4())
    try:
        response = await pipeline.process_voice_query(contents, file.filename or "audio.wav", request_id=req_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice query pipeline failure: {str(e)}")
