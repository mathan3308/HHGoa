import time
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.config import settings
from backend.app.core.logging import logger

class EmbeddingService:
    """
    Singleton-style Embedding service wrapping sentence-transformers.
    Loads model ONCE at startup and reuses it for all query/doc embeddings.
    Uses 'query: ' and 'passage: ' prefixes required for E5 embedding models.
    """
    _instance = None

    def __new__(cls, model_name: str = None):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = None):
        if self._initialized:
            return
        self.model_name = model_name or settings.EMBEDDING_MODEL
        logger.info(f"Initializing Embedding Model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Using fallback.")
            self.model = None
        self._initialized = True

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single search query with low latency."""
        if self.model is None:
            # Fallback pseudo-vector of dimension 384 for offline/mock development
            rng = np.random.RandomState(hash(query) % (2**32 - 1))
            vec = rng.randn(384).astype(np.float32)
            vec /= np.linalg.norm(vec)
            return vec.tolist()

        # E5 model instruction prefix
        formatted_query = f"query: {query}" if "e5" in self.model_name.lower() else query
        vec = self.model.encode(formatted_query, normalize_embeddings=True)
        return vec.tolist()

    def embed_documents(self, docs: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embeds a list of document chunks in batches."""
        if not docs:
            return []
        if self.model is None:
            results = []
            for d in docs:
                rng = np.random.RandomState(hash(d) % (2**32 - 1))
                vec = rng.randn(384).astype(np.float32)
                vec /= np.linalg.norm(vec)
                results.append(vec.tolist())
            return results

        formatted_docs = [f"passage: {d}" if "e5" in self.model_name.lower() else d for d in docs]
        embeddings = self.model.encode(formatted_docs, batch_size=batch_size, normalize_embeddings=True)
        return embeddings.tolist()
