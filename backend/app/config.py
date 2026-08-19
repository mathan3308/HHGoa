import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file dynamically whether running from root, backend, or Docker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATHS = [
    os.path.join(BASE_DIR, "..", ".env"),
    os.path.join(BASE_DIR, ".env"),
    "backend/.env",
    ".env"
]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATHS,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Sarvam AI Credentials & Models
    SARVAM_API_KEY: str = ""
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_LLM_MODEL: str = "sarvam-105b-conversations"

    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "msmarco_xi_full"

    # Embedding Model Config
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_BATCH_SIZE: int = 64
    QDRANT_BATCH_SIZE: int = 256

    # Dataset Configuration (Official AI4Bharat/MSMARCO-XI)
    DATASET_NAME: str = "ai4bharat/MSMARCO-XI"
    DATASET_CONFIG: str = "default"
    DATASET_LANGUAGES: str = "all"
    DATASET_SPLITS: str = "train,validation"
    DATASET_STREAMING: bool = True
    DATASET_MAX_RECORDS: Optional[int] = None
    DATASET_BATCH_SIZE: int = 256
    INGEST_MODE: str = "sample"

    # RAG & Chunking Parameters
    TOP_K: int = 10
    RRF_K: int = 60
    CHUNK_STRATEGY: str = "semantic"
    MAX_CONTEXT_CHUNKS: int = 5
    CHUNK_SIZE: int = 150
    CHUNK_OVERLAP: int = 30
    SEMANTIC_THRESHOLD: float = 0.75

    # Guardrails & Scoring Thresholds
    RETRIEVAL_THRESHOLD: float = 0.10
    GROUNDING_THRESHOLD: float = 0.60
    USE_RERANKER: bool = False

    # Application Settings
    ENVIRONMENT: str = "development"
    MOCK_EXTERNAL_SERVICES: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
