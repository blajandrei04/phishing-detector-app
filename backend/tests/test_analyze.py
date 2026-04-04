from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_analyze_valid_url():
    response = client.post("/api/analyze", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert 0.0 <= data["score"] <= 1.0
    assert data["verdict"] in {"phishing", "suspicious", "legitimate"}


def test_analyze_invalid_url():
    response = client.post("/api/analyze", json={"url": "not-a-url"})
    assert response.status_code == 422