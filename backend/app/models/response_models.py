from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LatencyBreakdown(BaseModel):
    stt_ms: float = Field(default=0.0, description="Speech-to-Text latency in milliseconds")
    embedding_ms: float = Field(default=0.0, description="Query embedding generation latency in ms")
    retrieval_ms: float = Field(default=0.0, description="Dense + Sparse + RRF retrieval latency in ms")
    reranking_ms: float = Field(default=0.0, description="Optional reranking module latency in ms")
    generation_ms: float = Field(default=0.0, description="LLM answer generation latency in ms")
    guardrail_ms: float = Field(default=0.0, description="Input + Relevance + Grounding guardrails latency in ms")
    total_rag_ms: float = Field(default=0.0, description="Total latency of the pure RAG engine (Embedding -> Guardrail)")
    total_end_to_end_ms: float = Field(default=0.0, description="Total end-to-end pipeline latency including STT")

class GroundingResult(BaseModel):
    grounded: bool = Field(..., description="Whether the generated response is strictly grounded in retrieved context")
    reason: Optional[str] = Field(default=None, description="Explanation or fallback rationale")
    confidence: Optional[float] = Field(default=None, description="Confidence score (null if unsupported)")

class SourceChunk(BaseModel):
    chunk_id: str
    source_id: str
    passage_id: Optional[str] = None
    query_id: Optional[str] = None
    language: str = "en"
    text: str
    relevance_score: float
    chunk_strategy: str

class VoiceQueryResponse(BaseModel):
    request_id: str
    transcript: str
    language: str
    answer: str
    grounded: bool
    grounding_details: Optional[GroundingResult] = None
    sources: List[SourceChunk] = Field(default_factory=list)
    latency: LatencyBreakdown
    status: str = "success"
    error: Optional[str] = None
    mock_mode: bool = False

class TranscriptResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None
    latency_ms: float

class SearchResultItem(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    latency_ms: float

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    mock_mode: bool
