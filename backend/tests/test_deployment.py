from fastapi.testclient import TestClient

import backend.app.main as main
from backend.app.main import create_app


async def no_checks(claims):
    return []


def test_verify_rejects_text_shorter_than_10_characters(monkeypatch):
    monkeypatch.setattr(main, "run_all_checks", no_checks)
    client = TestClient(create_app())

    response = client.post("/api/verify", json={"text": "123456789"})

    assert response.status_code == 422
    assert "at least 10 characters" in response.json()["detail"][0]["msg"]


def test_verify_rejects_text_longer_than_5000_characters(monkeypatch):
    monkeypatch.setattr(main, "run_all_checks", no_checks)
    client = TestClient(create_app())

    response = client.post("/api/verify", json={"text": "x" * 5001})

    assert response.status_code == 422
    assert "no more than 5000 characters" in response.json()["detail"][0]["msg"]


def test_verify_accepts_minimum_and_maximum_text_lengths(monkeypatch):
    monkeypatch.setattr(main, "run_all_checks", no_checks)
    client = TestClient(create_app())

    minimum_response = client.post("/api/verify", json={"text": "1234567890"})
    maximum_response = client.post("/api/verify", json={"text": "x" * 5000})

    assert minimum_response.status_code == 200
    assert maximum_response.status_code == 200
    assert "checks" in minimum_response.json()
    assert "checks" in maximum_response.json()


def test_verify_rate_limit_is_20_requests_per_minute_per_ip(monkeypatch):
    monkeypatch.setattr(main, "run_all_checks", no_checks)
    client = TestClient(create_app())

    for _ in range(20):
        response = client.post("/api/verify", json={"text": "Valid offer text"})
        assert response.status_code == 200

    limited_response = client.post("/api/verify", json={"text": "Valid offer text"})

    assert limited_response.status_code == 429
    assert "wait a minute" in limited_response.json()["detail"]