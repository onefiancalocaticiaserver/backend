from fastapi.testclient import TestClient

from app.api.v1.endpoints import health as health_module
from app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "one-api"}


def test_health_db_endpoint_ok(monkeypatch) -> None:
    monkeypatch.setattr(health_module, "check_database_connection", lambda: True)
    client = TestClient(create_app())

    response = client.get("/v1/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_db_endpoint_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(health_module, "check_database_connection", lambda: False)
    client = TestClient(create_app())

    response = client.get("/v1/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "database_unavailable"}
