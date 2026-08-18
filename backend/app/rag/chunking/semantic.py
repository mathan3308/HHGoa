from typing import List, Optional
import numpy as np
from backend.app.utils.text import split_into_sentences

class SemanticChunkingStrategy:
    """
    Semantic chunking:
    1. Split text into sentences.
    2. Compute embeddings/similarity between consecutive sentences.
    3. Group sentences while similarity remains above threshold.
    4. Start new chunk when semantic similarity drops below similarity_threshold.
    """
    def __init__(self, similarity_threshold: float = 0.75, embedding_service = None):
        self.similarity_threshold = similarity_threshold
        self.embedding_service = embedding_service

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def _simple_text_similarity(self, s1: str, s2: str) -> float:
        """Fast fallback word-jaccard similarity if embedding model is offline."""
        w1 = set(s1.lower().split())
        w2 = set(s2.lower().split())
        if not w1 or not w2:
            return 0.0
        intersection = len(w1.intersection(w2))
        union = len(w1.union(w2))
        return intersection / union if union > 0 else 0.0

    def chunk(self, text: str, embedding_service=None) -> List[str]:
        sentences = split_into_sentences(text)
        if not sentences:
            return []
        if len(sentences) == 1:
            return sentences

        service = embedding_service or self.embedding_service

        embeddings = None
        if service is not None:
            try:
                # Batch embed sentences
                embeddings = service.embed_documents(sentences)
            except Exception:
                embeddings = None

        chunks = []
        current_chunk = [sentences[0]]

        for i in range(len(sentences) - 1):
            s_curr = sentences[i]
            s_next = sentences[i + 1]

            if embeddings is not None and i + 1 < len(embeddings):
                sim = self._cosine_similarity(np.array(embeddings[i]), np.array(embeddings[i + 1]))
            else:
                sim = self._simple_text_similarity(s_curr, s_next)

            # If similarity drops below threshold, finalize current chunk
            if sim < self.similarity_threshold and len(" ".join(current_chunk).split()) >= 30:
                chunks.append(" ".join(current_chunk))
                current_chunk = [s_next]
            else:
                current_chunk.append(s_next)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
