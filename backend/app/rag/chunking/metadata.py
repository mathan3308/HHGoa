from typing import List, Dict, Any, Optional
import uuid
from backend.app.rag.chunking.fixed import FixedChunkingStrategy
from backend.app.rag.chunking.sentence import SentenceChunkingStrategy
from backend.app.rag.chunking.semantic import SemanticChunkingStrategy

class MetadataAwareChunkingStrategy:
    """
    Wraps underlying chunking strategy and attaches standardized metadata:
    - language
    - query_id
    - query_type
    - source_id
    - passage_id
    - chunk_strategy
    - chunk_index
    """
    def __init__(self, strategy_name: str = "semantic", **kwargs):
        self.strategy_name = strategy_name.lower()
        if self.strategy_name == "fixed":
            self.strategy = FixedChunkingStrategy(
                chunk_size=kwargs.get("chunk_size", 150),
                overlap=kwargs.get("overlap", 30)
            )
        elif self.strategy_name == "sentence":
            self.strategy = SentenceChunkingStrategy(
                sentences_per_chunk=kwargs.get("sentences_per_chunk", 3),
                sentence_overlap=kwargs.get("sentence_overlap", 1)
            )
        else:
            self.strategy = SemanticChunkingStrategy(
                similarity_threshold=kwargs.get("semantic_threshold", 0.75),
                embedding_service=kwargs.get("embedding_service", None)
            )

    def chunk_with_metadata(
        self,
        text: str,
        source_id: str,
        language: str = "en",
        query_id: Optional[str] = None,
        query_type: Optional[str] = None,
        passage_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        raw_chunks = self.strategy.chunk(text)
        chunk_objects = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_id = f"{source_id}_c{idx}_{uuid.uuid4().hex[:6]}"
            meta = {
                "chunk_id": chunk_id,
                "text": chunk_text,
                "language": language,
                "query_id": query_id or "",
                "query_type": query_type or "",
                "source_id": source_id,
                "passage_id": passage_id or source_id,
                "chunk_strategy": self.strategy_name,
                "chunk_index": idx,
                "total_chunks": len(raw_chunks),
            }
            if extra_metadata:
                meta.update(extra_metadata)
            chunk_objects.append(meta)

        return chunk_objects
