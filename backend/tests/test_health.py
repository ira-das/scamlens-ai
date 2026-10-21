# backend/tests/test_health.py
from fastapi.testclient import TestClient

from backend.app.main import app, create_app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_default_cors_origins_are_allowed(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    client = TestClient(create_app())

    for origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
        response = client.options(
            "/api/verify",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_regex_allows_preview_origin(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGIN_REGEX", r"https://[a-z0-9-]+\.vercel\.app")
    client = TestClient(create_app())

    response = client.options(
        "/api/verify",
        headers={
            "Origin": "https://scamlens-preview.vercel.app",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://scamlens-preview.vercel.app"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_wildcard_origin_disables_credentials(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "*")
    monkeypatch.delenv("ALLOWED_ORIGIN_REGEX", raising=False)
    client = TestClient(create_app())

    response = client.options(
        "/api/verify",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in response.headers