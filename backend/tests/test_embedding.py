from backend.app.services.embedding_service import EmbeddingService

def test_embedding_query():
    service = EmbeddingService()
    vec = service.embed_query("What is the capital of India?")
    assert isinstance(vec, list)
    assert len(vec) in (384, 768, 1024)

def test_embedding_documents():
    service = EmbeddingService()
    docs = ["Doc one text.", "Doc two text."]
    embs = service.embed_documents(docs)
    assert len(embs) == 2
    assert len(embs[0]) == len(embs[1])
