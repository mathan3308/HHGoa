from typing import List
from backend.app.utils.text import normalize_text

class FixedChunkingStrategy:
    """Fixed-size word chunking with configurable overlap."""
    def __init__(self, chunk_size: int = 150, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        text = normalize_text(text)
        words = text.split()
        if not words:
            return []

        chunks = []
        step = self.chunk_size - self.overlap
        if step <= 0:
            step = max(1, self.chunk_size // 2)

        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_str = " ".join(chunk_words)
            if chunk_str:
                chunks.append(chunk_str)
            if i + self.chunk_size >= len(words):
                break

        return chunks
