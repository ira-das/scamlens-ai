from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace

from backend.app import tinyfish_client
from backend.app.checks import verification_checks
from backend.app.checks.verification_checks import run_check_domain


class FakeAgent:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeSearch:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeFetch:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get_contents(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_agent_domain_check_uses_public_whois_lookup(monkeypatch):
    agent = FakeAgent(
        SimpleNamespace(
            status="COMPLETED",
            result={"age_days": 12, "registration_date": "2026-10-01"},
            error=None,
        )
    )
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(
        tinyfish_client,
        "_create_client",
        lambda: SimpleNamespace(agent=agent),
    )

    result = tinyfish_client.web_agent(domain="example.com")

    assert result["age_days"] == 12
    assert result["status"] == "bad"
    assert agent.calls[0]["url"] == "https://who.is/whois/example.com"
    assert result["evidence"][0]["url"] == agent.calls[0]["url"]


def test_search_results_become_evidence_links(monkeypatch):
    search = FakeSearch(
        SimpleNamespace(
            results=[
                SimpleNamespace(
                    title="Internship scam complaints",
                    snippet="Several users report a registration fee scam.",
                    url="https://reports.example/scam",
                )
            ]
        )
    )
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(
        tinyfish_client,
        "_create_client",
        lambda: SimpleNamespace(search=search),
    )

    result = tinyfish_client.search(domain="example.com", fee_demanded=0)

    assert result["status"] == "bad"
    assert result["evidence"][0]["url"] == "https://reports.example/scam"
    assert "example.com" in search.calls[0]["query"]


def test_company_fetch_uses_claimed_domain(monkeypatch):
    fetch = FakeFetch(
        SimpleNamespace(
            results=[
                SimpleNamespace(
                    url="https://example.com",
                    title="Example Careers",
                    text="Example careers and internship opportunities.",
                )
            ],
            errors=[],
        )
    )
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(
        tinyfish_client,
        "_create_client",
        lambda: SimpleNamespace(fetch=fetch),
    )

    result = tinyfish_client.fetch(company="Example", domain="example.com")

    assert result["status"] == "ok"
    assert fetch.calls[0]["urls"] == ["https://example.com"]
    assert result["evidence"][0]["url"] == "https://example.com"


def test_agent_failure_is_isolated_to_one_check(monkeypatch):
    agent = FakeAgent(
        SimpleNamespace(
            status="FAILED",
            result=None,
            error={"code": "SITE_BLOCKED", "message": "Target site was blocked."},
        )
    )
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", False)
    monkeypatch.setattr(
        tinyfish_client,
        "_create_client",
        lambda: SimpleNamespace(agent=agent),
    )

    check = asyncio.run(run_check_domain("example.com"))

    assert check.status == "error"
    assert check.name == "Domain Age & Registration"


def test_company_page_check_uses_fetch_adapter(monkeypatch):
    called = {}

    def fake_fetch(**kwargs):
        called.update(kwargs)
        return {
            "status": "ok",
            "summary": "Company page checked.",
            "risk_points": 0,
            "max_points": 10,
            "evidence": [],
        }

    monkeypatch.setattr(verification_checks, "fetch", fake_fetch)

    check = asyncio.run(verification_checks.run_check_company_page("Example", "example.com"))

    assert called == {"company": "Example", "domain": "example.com"}
    assert check.tool_used == "TinyFish Fetch"


def test_adapter_timeout_becomes_error_result(monkeypatch):
    monkeypatch.setattr(verification_checks, "AGENT_TIMEOUT_SECONDS", 0.01)

    def slow_adapter(**kwargs):
        time.sleep(0.05)
        return {"status": "ok", "summary": "late", "risk_points": 0, "evidence": []}

    check = asyncio.run(
        verification_checks._call_adapter(slow_adapter, 0.01, 25, domain="example.com")
    )

    assert check["status"] == "error"
    assert "timed out" in check["summary"]


def test_mock_domain_lookup_keeps_deterministic_verdict(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", True)

    first = tinyfish_client.web_agent(domain="internship-portal.xyz")
    second = tinyfish_client.web_agent(domain="internship-portal.xyz")

    assert first["status"] == second["status"] == "bad"
    assert first["risk_points"] == second["risk_points"] == 25
    assert first["evidence"][0]["url"] == second["evidence"][0]["url"]