import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["service"] == "api-gateway"


def test_token_valid_credentials(client):
    resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin-secret"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_token_invalid_credentials(client):
    resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_protected_route_requires_auth(client):
    resp = client.get("/api/v1/transactions/")
    assert resp.status_code == 401
