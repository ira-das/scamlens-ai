from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from backend.app import tinyfish_client
from backend.app.checks import verification_checks
from backend.app import main as main_module
from backend.app.main import create_app, resolve_runtime_mode
from backend.app.models import ClaimExtraction


async def no_checks(claims):
    return []


def test_default_mode_is_mock(monkeypatch):
    monkeypatch.delenv("USE_MOCKS", raising=False)
    monkeypatch.delenv("TINYFISH_API_KEY", raising=False)

    assert resolve_runtime_mode() == "mock"


@pytest.mark.parametrize("false_value", ["false", "0", "no"])
def test_live_mode_without_key_falls_back_to_mock(monkeypatch, caplog, false_value):
    monkeypatch.setenv("USE_MOCKS", false_value)
    monkeypatch.delenv("TINYFISH_API_KEY", raising=False)

    assert resolve_runtime_mode() == "mock"
    client = TestClient(create_app())
    assert client.get("/health").json()["mode"] == "mock"
    assert tinyfish_client.USE_MOCKS is True
    assert "Live mode requested but TINYFISH_API_KEY is not set; using mocks" in caplog.text


def test_live_summary_is_selected_without_making_external_calls(monkeypatch):
    monkeypatch.setenv("USE_MOCKS", "false")
    monkeypatch.setenv("TINYFISH_API_KEY", "test-placeholder")
    monkeypatch.setattr(main_module, "run_all_checks", no_checks)
    client = TestClient(create_app())

    response = client.post("/api/verify", json={"text": "A sufficiently long offer"})

    assert response.status_code == 200
    assert response.json()["summary"] == "Offer reviewed with live TinyFish checks."


def test_health_response_includes_runtime_mode(monkeypatch):
    monkeypatch.setenv("USE_MOCKS", "true")
    monkeypatch.delenv("TINYFISH_API_KEY", raising=False)
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "mock"}


def test_one_live_check_failure_does_not_fail_other_checks(monkeypatch):
    monkeypatch.setenv("USE_MOCKS", "false")
    monkeypatch.setenv("TINYFISH_API_KEY", "test-placeholder")
    monkeypatch.setenv("DISABLE_AGENT_CHECKS", "false")
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(tinyfish_client, "DISABLE_AGENT_CHECKS", False)
    monkeypatch.setattr(
        main_module,
        "extract_claims_regex",
        lambda text: ClaimExtraction(
            company="Example",
            domain="example.com",
            recruiter_name="Taylor Example",
            stipend=10000,
            address="Bengaluru",
            fee_demanded=0,
        ),
    )

    def failing_rdap(**kwargs):
        raise RuntimeError("private upstream details")

    def successful_agent(**kwargs):
        return {
            "status": "ok",
            "summary": "Plausibility check completed.",
            "risk_points": 0,
            "max_points": 15,
            "evidence": [],
        }

    def successful_fetch(**kwargs):
        return {
            "status": "ok",
            "summary": "Fetch completed.",
            "risk_points": 0,
            "max_points": 15 if kwargs.get("recruiter_name") else 10,
            "evidence": [],
        }

    def successful_search(**kwargs):
        return {
            "status": "ok",
            "summary": "Search completed.",
            "risk_points": 0,
            "max_points": 25,
            "evidence": [],
        }

    monkeypatch.setattr(verification_checks, "lookup_domain_registration", failing_rdap)
    monkeypatch.setattr(verification_checks, "web_agent", successful_agent)
    monkeypatch.setattr(verification_checks, "fetch", successful_fetch)
    monkeypatch.setattr(verification_checks, "search", successful_search)

    client = TestClient(create_app())
    response = client.post(
        "/api/verify",
        json={
            "text": "A role at Example, domain example.com, stipend INR 10000, address Bengaluru."
        },
    )

    assert response.status_code == 200
    report = response.json()
    checks = report["checks"]
    assert len(checks) == 5
    failed_checks = [check for check in checks if check["status"] == "error"]
    successful_checks = [check for check in checks if check["status"] == "ok"]
    assert len(failed_checks) == 1
    assert len(successful_checks) == 4
    assert all(check["risk_points"] == 0 for check in failed_checks)
    assert all("private upstream details" not in check["summary"] for check in failed_checks)
    assert isinstance(report["risk_score"], int)
    assert report["level"] in {"LOW RISK", "MEDIUM RISK", "HIGH RISK"}


def test_disabled_agent_checks_never_call_agent(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "DISABLE_AGENT_CHECKS", True)
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)

    def unexpected_agent_call(**kwargs):
        raise AssertionError("Agent adapter must not be called")

    monkeypatch.setattr(tinyfish_client, "_run_plausibility_agent", unexpected_agent_call)

    result = tinyfish_client.web_agent(stipend=12000, address="Bengaluru")

    assert result["status"] == "error"
    assert result["risk_points"] == 0
    assert result["summary"] == "Agent checks disabled"