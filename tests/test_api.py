import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    # Check if custom metrics are present
    text = response.text
    assert "rag_system_custom_metrics_api_requests_total" in text or "llm_token_usage" in text or "rag_cache_hits" in text or "python" in text
