from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List

from backend.app.models import CheckResult
from backend.app.tinyfish_client import (
    AGENT_TIMEOUT_SECONDS,
    FETCH_TIMEOUT_SECONDS,
    SEARCH_TIMEOUT_SECONDS,
    fetch,
    search,
    web_agent,
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _call_adapter(
    operation: Callable[..., Dict[str, Any]],
    timeout_seconds: int,
    max_points: int,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run the synchronous TinyFish SDK without blocking the async event loop."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(operation, **kwargs),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "summary": "TinyFish check timed out.",
            "risk_points": 0,
            "max_points": max_points,
            "evidence": [],
        }
    except Exception:
        return {
            "status": "error",
            "summary": "TinyFish check failed.",
            "risk_points": 0,
            "max_points": max_points,
            "evidence": [],
        }


def _check_result(
    name: str,
    tool_used: str,
    raw: Dict[str, Any],
    max_points: int,
) -> CheckResult:
    evidence = []
    for item in raw.get("evidence", []):
        if not isinstance(item, dict) or not item.get("url"):
            continue
        evidence.append(
            {
                "label": str(item.get("label") or "Source"),
                "url": str(item["url"]),
                "retrieved_at": str(item.get("retrieved_at") or _iso_now()),
            }
        )
    return CheckResult(
        name=name,
        tool_used=tool_used,
        status=raw.get("status", "error"),
        summary=raw.get("summary", "Unable to complete this check."),
        risk_points=int(raw.get("risk_points", 0)),
        max_points=int(raw.get("max_points", max_points)),
        evidence=evidence,
    )


async def run_check_domain(domain: str) -> CheckResult:
    raw = await _call_adapter(
        web_agent,
        AGENT_TIMEOUT_SECONDS,
        25,
        domain=domain,
    )
    return _check_result("Domain Age & Registration", "TinyFish Web Agent", raw, 25)


async def run_check_company_page(company: str, domain: str | None = None) -> CheckResult:
    raw = await _call_adapter(
        fetch,
        FETCH_TIMEOUT_SECONDS,
        10,
        company=company,
        domain=domain,
    )
    return _check_result("Company & Careers Page Check", "TinyFish Fetch", raw, 10)


async def run_check_recruiter(recruiter_name: str, domain: str) -> CheckResult:
    raw = await _call_adapter(
        fetch,
        FETCH_TIMEOUT_SECONDS,
        15,
        recruiter_name=recruiter_name,
        domain=domain,
    )
    return _check_result("Recruiter Verification", "TinyFish Fetch", raw, 15)


async def run_check_scam_reports(domain: str, fee_demanded: int) -> CheckResult:
    raw = await _call_adapter(
        search,
        SEARCH_TIMEOUT_SECONDS,
        25,
        domain=domain,
        fee_demanded=fee_demanded,
    )
    return _check_result("Scam & Employee Review Reports", "TinyFish Search", raw, 25)


async def run_check_address_and_stipend(
    stipend: int | None,
    address: str | None,
    domain: str | None = None,
) -> CheckResult:
    raw = await _call_adapter(
        web_agent,
        AGENT_TIMEOUT_SECONDS,
        15,
        stipend=stipend,
        address=address,
        company_domain=domain,
    )
    return _check_result("Address & Stipend Plausibility", "TinyFish Web Agent", raw, 15)


async def run_all_checks(claims: Dict[str, Any]) -> List[CheckResult]:
    domain = claims.get("domain")
    company = claims.get("company")
    recruiter_name = claims.get("recruiter_name")
    stipend = claims.get("stipend")
    address = claims.get("address")
    fee_demanded = claims.get("fee_demanded") or 0

    return await asyncio.gather(
        run_check_domain(domain) if domain else asyncio.sleep(0, result=CheckResult(
            name="Domain Age & Registration",
            tool_used="TinyFish Web Agent",
            status="error",
            summary="Domain is unknown; lookup skipped.",
            risk_points=0,
            max_points=25,
        )),
        run_check_company_page(company, domain) if company or domain else asyncio.sleep(0, result=CheckResult(
            name="Company & Careers Page Check",
            tool_used="TinyFish Fetch",
            status="error",
            summary="Company could not be identified; lookup skipped.",
            risk_points=0,
            max_points=10,
        )),
        run_check_recruiter(recruiter_name, domain) if recruiter_name and domain else asyncio.sleep(0, result=CheckResult(
            name="Recruiter Verification",
            tool_used="TinyFish Fetch",
            status="error",
            summary="Recruiter or company domain is unknown; lookup skipped.",
            risk_points=0,
            max_points=15,
        )),
        run_check_scam_reports(domain, fee_demanded) if domain or fee_demanded else asyncio.sleep(0, result=CheckResult(
            name="Scam & Employee Review Reports",
            tool_used="TinyFish Search",
            status="error",
            summary="Domain is unknown and no fee was detected; lookup skipped.",
            risk_points=0,
            max_points=25,
        )),
        run_check_address_and_stipend(stipend, address, domain) if stipend is not None or address else asyncio.sleep(0, result=CheckResult(
            name="Address & Stipend Plausibility",
            tool_used="TinyFish Web Agent",
            status="error",
            summary="Address and stipend are unknown; lookup skipped.",
            risk_points=0,
            max_points=15,
        )),
    )