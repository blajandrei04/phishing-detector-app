from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user
from app.db.models import User
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth():
    dummy_user = User(id=1, username="testuser", email="test@example.com", hashed_password="mocked_password")
    app.dependency_overrides[get_current_user] = lambda: dummy_user
    yield
    app.dependency_overrides.clear()


def test_analyze_valid_url():
    response = client.post("/api/analyze", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert 0.0 <= data["score"] <= 1.0
    assert data["verdict"] in {"phishing", "suspicious", "legitimate"}


def test_analyze_invalid_url():
    response = client.post("/api/analyze", json={"url": "not-a-url"})
    # Since the request model enforces a valid URL, it should be 422 if it fails pydantic validation,
    # or if we allow it, it will run. Let's see what status code is expected.
    # The previous test asserted 422, let's keep it.
    assert response.status_code == 422