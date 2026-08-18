import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "api" in data["services"]

def test_text_query_endpoint():
    payload = {"query": "What is the capital of India?", "language": "en"}
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "latency" in data
    assert "grounded" in data
    assert data["status"] in ("completed", "rejected")

def test_search_endpoint():
    payload = {"query": "Qdrant vector database", "top_k": 5}
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "latency_ms" in data

def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
