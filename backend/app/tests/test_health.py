from fastapi.testclient import TestClient

from app import create_app


def test_health_endpoint_returns_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
