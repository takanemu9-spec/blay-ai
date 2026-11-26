from fastapi.testclient import TestClient
from app.main import app


def test_plan_endpoint_rejects_missing_api_key(monkeypatch):
    monkeypatch.setenv("BLAY_API_KEY", "test-secret-key")

    client = TestClient(app)

    response = client.post(
        "/plan",
        json={"prompt": "Test keamanan BLAY"}
    )

    assert response.status_code == 401
