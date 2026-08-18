from typing import List
from backend.app.utils.text import split_into_sentences

class SentenceChunkingStrategy:
    """Sentence-boundary chunking grouping a target number of sentences per chunk."""
    def __init__(self, sentences_per_chunk: int = 3, sentence_overlap: int = 1):
        self.sentences_per_chunk = sentences_per_chunk
        self.sentence_overlap = sentence_overlap

    def chunk(self, text: str) -> List[str]:
        sentences = split_into_sentences(text)
        if not sentences:
            return []

        chunks = []
        step = self.sentences_per_chunk - self.sentence_overlap
        if step <= 0:
            step = 1

        for i in range(0, len(sentences), step):
            group = sentences[i : i + self.sentences_per_chunk]
            chunk_str = " ".join(group)
            if chunk_str:
                chunks.append(chunk_str)
            if i + self.sentences_per_chunk >= len(sentences):
                break

        return chunks
