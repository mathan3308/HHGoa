from backend.app.rag.chunking.fixed import FixedChunkingStrategy
from backend.app.rag.chunking.sentence import SentenceChunkingStrategy
from backend.app.rag.chunking.semantic import SemanticChunkingStrategy
from backend.app.rag.chunking.metadata import MetadataAwareChunkingStrategy

def test_fixed_chunking():
    text = "Word " * 300
    chunker = FixedChunkingStrategy(chunk_size=100, overlap=20)
    chunks = chunker.chunk(text)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 100 for c in chunks)

def test_sentence_chunking():
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    chunker = SentenceChunkingStrategy(sentences_per_chunk=2, sentence_overlap=1)
    chunks = chunker.chunk(text)
    assert len(chunks) > 1

def test_semantic_chunking():
    text = "New Delhi is the capital of India. It has parliament. Vector databases index text embeddings. Qdrant uses Rust."
    chunker = SemanticChunkingStrategy(similarity_threshold=0.5)
    chunks = chunker.chunk(text)
    assert len(chunks) >= 1

def test_metadata_aware_chunking():
    text = "Test passage content for metadata chunking."
    chunker = MetadataAwareChunkingStrategy(strategy_name="fixed")
    chunks = chunker.chunk_with_metadata(text, source_id="source_123", language="en")
    assert len(chunks) >= 1
    assert chunks[0]["source_id"] == "source_123"
    assert chunks[0]["language"] == "en"
    assert "chunk_id" in chunks[0]
