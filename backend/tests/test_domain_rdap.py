from __future__ import annotations

from datetime import date, timedelta

import httpx
import pytest

from backend.app import tinyfish_client


class FakeRdapResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://rdap.org/domain/example.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("RDAP failed", request=request, response=response)


def rdap_payload(days_old: int) -> dict:
    registered = (date.today() - timedelta(days=days_old)).isoformat()
    return {
        "events": [
            {"eventAction": "last changed", "eventDate": "2026-10-20T00:00:00Z"},
            {"eventAction": "registration", "eventDate": f"{registered}T00:00:00Z"},
        ]
    }


@pytest.mark.parametrize(
    ("days_old", "expected_status", "expected_points"),
    [(30, "bad", 25), (100, "warn", 10), (500, "ok", 0)],
)
def test_rdap_registration_age_thresholds(monkeypatch, days_old, expected_status, expected_points):
    calls = []

    def fake_get(url, *, follow_redirects, timeout):
        calls.append((url, follow_redirects, timeout))
        return FakeRdapResponse(200, rdap_payload(days_old))

    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(tinyfish_client.httpx, "get", fake_get)

    result = tinyfish_client.lookup_domain_registration("example.com")

    assert calls == [("https://rdap.org/domain/example.com", True, 8.0)]
    assert result["status"] == expected_status
    assert result["risk_points"] == expected_points
    assert result["summary"] == (
        f"Domain registered on {(date.today() - timedelta(days=days_old)).isoformat()} "
        f"({days_old} days ago)."
    )
    assert result["evidence"][0]["url"] == "https://rdap.org/domain/example.com"


@pytest.mark.parametrize(
    "response",
    [
        FakeRdapResponse(200, {"events": [{"eventAction": "last changed", "eventDate": "2026-10-20"}]}),
        FakeRdapResponse(404, {}),
    ],
)
def test_rdap_missing_registration_record_is_warning(monkeypatch, response):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(tinyfish_client.httpx, "get", lambda *args, **kwargs: response)

    result = tinyfish_client.lookup_domain_registration("example.com")

    assert result["status"] == "warn"
    assert result["risk_points"] == 10
    assert result["summary"] == "No registration record found for this domain; treat as suspicious."
    assert result["evidence"][0]["url"] == "https://rdap.org/domain/example.com"


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
def test_rdap_network_error_returns_error_without_fake_age(monkeypatch, error_type):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)

    def fail_request(*args, **kwargs):
        raise error_type("private network details")

    monkeypatch.setattr(tinyfish_client.httpx, "get", fail_request)

    result = tinyfish_client.lookup_domain_registration("example.com")

    assert result["status"] == "error"
    assert result["risk_points"] == 0
    assert result["summary"] == "Domain registration lookup failed."
    assert "0 days old" not in result["summary"]


def test_domain_check_uses_synthetic_rdap_event_in_mock_mode(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", True)

    def unexpected_http_call(*args, **kwargs):
        raise AssertionError("Mock mode must not make an RDAP request")

    monkeypatch.setattr(tinyfish_client.httpx, "get", unexpected_http_call)

    result = tinyfish_client.lookup_domain_registration("internship-portal.xyz")

    assert result["status"] == "bad"
    assert result["risk_points"] == 25
    assert "days ago" in result["summary"]