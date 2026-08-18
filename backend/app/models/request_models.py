from pydantic import BaseModel, Field
from typing import Optional

class TextQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Text question/query for the RAG pipeline.")
    language: Optional[str] = Field(default="en", description="Language code (e.g. en, hi, ta, te).")
    chunk_strategy: Optional[str] = Field(default=None, description="Override chunking strategy for retrieval filtering.")
    top_k: Optional[int] = Field(default=None, description="Number of top contexts to retrieve.")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query string for dense/sparse search.")
    top_k: Optional[int] = Field(default=10, description="Top K results to return.")
    chunk_strategy: Optional[str] = Field(default=None, description="Filter by chunk strategy.")
    language: Optional[str] = Field(default=None, description="Filter by language code.")

class BenchmarkRunRequest(BaseModel):
    num_queries: int = Field(default=50, ge=5, le=500, description="Number of test queries to run for latency evaluation.")
    chunk_strategy: Optional[str] = Field(default="semantic", description="Chunk strategy to benchmark.")
