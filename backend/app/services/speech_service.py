import httpx
import time
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.exceptions import STTException
from backend.app.core.logging import logger
from backend.app.models.response_models import TranscriptResponse

class BaseSpeechProvider:
    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> TranscriptResponse:
        raise NotImplementedError

class SarvamSpeechProvider(BaseSpeechProvider):
    """Sarvam AI Saaras v3 Speech-to-Text provider."""
    def __init__(self, api_key: str, model: str = "saaras:v3"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.sarvam.ai/speech-to-text"

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> TranscriptResponse:
        if not self.api_key:
            raise STTException("SARVAM_API_KEY is not configured.")

        headers = {"api-subscription-key": self.api_key}
        files = {"file": (filename, audio_bytes, "audio/wav")}
        data = {"model": self.model, "language_code": "unknown"}

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.url, headers=headers, files=files, data=data)
                latency_ms = round((time.perf_counter() - start) * 1000.0, 2)

                if response.status_code == 200:
                    res_json = response.json()
                    transcript = res_json.get("transcript", res_json.get("text", "")).strip()
                    detected_lang = res_json.get("language_code", "en")
                    # If API does not return confidence, return null rather than inventing a value
                    confidence = res_json.get("confidence", None)
                    return TranscriptResponse(
                        text=transcript,
                        language=detected_lang,
                        confidence=confidence,
                        latency_ms=latency_ms
                    )
                else:
                    raise STTException(f"Sarvam STT API error {response.status_code}: {response.text}")
            except httpx.HTTPError as e:
                raise STTException(f"HTTP request to Sarvam STT failed: {str(e)}")

class MockSpeechProvider(BaseSpeechProvider):
    """Mock Speech-to-Text provider for development and testing."""
    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> TranscriptResponse:
        await httpx.AsyncClient().get("http://httpbin.org/delay/0", timeout=1.0)
        return TranscriptResponse(
            text="What are the key details in the MSMARCO Indian language dataset?",
            language="en",
            confidence=0.98,
            latency_ms=45.0
        )

class SpeechService:
    def __init__(self):
        if settings.MOCK_EXTERNAL_SERVICES or not settings.SARVAM_API_KEY:
            self.provider = MockSpeechProvider()
        else:
            self.provider = SarvamSpeechProvider(
                api_key=settings.SARVAM_API_KEY,
                model=settings.SARVAM_STT_MODEL
            )

    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.wav") -> TranscriptResponse:
        return await self.provider.transcribe(audio_bytes, filename)
