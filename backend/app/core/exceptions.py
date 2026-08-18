class BaseVoiceRAGException(Exception):
    """Base exception for Voice RAG Pipeline."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class STTException(BaseVoiceRAGException):
    """Exception during Speech-To-Text processing."""
    def __init__(self, message: str = "Speech-to-Text conversion failed", status_code: int = 502, details: dict = None):
        super().__init__(message, status_code, details)

class RetrievalException(BaseVoiceRAGException):
    """Exception during context retrieval or vector store query."""
    def __init__(self, message: str = "Retrieval service error", status_code: int = 500, details: dict = None):
        super().__init__(message, status_code, details)

class LLMException(BaseVoiceRAGException):
    """Exception during answer generation."""
    def __init__(self, message: str = "LLM generation failed", status_code: int = 502, details: dict = None):
        super().__init__(message, status_code, details)

class GuardrailException(BaseVoiceRAGException):
    """Exception when request or response violates guardrails."""
    def __init__(self, message: str = "Guardrail violation", status_code: int = 400, details: dict = None):
        super().__init__(message, status_code, details)

class InvalidAudioException(BaseVoiceRAGException):
    """Exception when provided audio file is invalid, corrupt, or oversized."""
    def __init__(self, message: str = "Invalid audio file format or size", status_code: int = 400, details: dict = None):
        super().__init__(message, status_code, details)
