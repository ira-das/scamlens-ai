from __future__ import annotations

from typing import Any, List, Tuple

# Range assumptions from the brief
STIPEND_LOWER_BOUND = 5000
STIPEND_UPPER_BOUND = 25000
STIPEND_CAUTION = 25000
STIPEND_UNUSUAL = 40000

WEIGHTS = {
    "domain": 25,
    "review_reports": 25,
    "recruiter": 15,
    "address_stipend": 15,
    "company_page": 10,
    "gemini_patterns": 10,
}

RISK_LEVELS = (
    (29, "LOW RISK"),
    (69, "MEDIUM RISK"),
    (100, "HIGH RISK"),
)


def compute_risk_score(
    domain_risk: int,
    review_risk: int,
    recruiter_risk: int,
    address_stipend_risk: int,
    company_page_risk: int,
    gemini_pattern_risk: int,
) -> int:
    total = (
        domain_risk
        + review_risk
        + recruiter_risk
        + address_stipend_risk
        + company_page_risk
        + gemini_pattern_risk
    )
    return min(total, 100)


def get_level(score: int) -> str:
    if score <= 29:
        return "LOW RISK"
    if score <= 69:
        return "MEDIUM RISK"
    return "HIGH RISK"


def _claims_dict(claims: Any) -> dict[str, Any]:
    if hasattr(claims, "model_dump"):
        return claims.model_dump()
    return claims if isinstance(claims, dict) else {}


def claim_risk_points(claims: Any = None) -> int:
    claim_data = _claims_dict(claims)
    flags = {str(flag).lower() for flag in claim_data.get("scam_wording_flags", [])}
    points = 25 if int(claim_data.get("fee_demanded") or 0) > 0 else 0
    if flags.intersection({"aadhaar", "otp"}):
        points += 15
    if "no_interview" in flags:
        points += 10
    if "private_chat" in flags:
        points += 10
    if "urgency" in flags:
        points += 5
    return points


def claim_red_flags(claims: Any = None) -> list[str]:
    claim_data = _claims_dict(claims)
    flags = {str(flag).lower() for flag in claim_data.get("scam_wording_flags", [])}
    red_flags = []
    fee_demanded = int(claim_data.get("fee_demanded") or 0)
    if fee_demanded > 0:
        red_flags.append(f"Upfront payment of ₹{fee_demanded} demanded.")
    if flags.intersection({"aadhaar", "otp"}):
        red_flags.append("The offer requests sensitive identity or account details.")
    if "no_interview" in flags:
        red_flags.append("The offer says no interview or screening is required.")
    if "private_chat" in flags:
        red_flags.append("The offer asks to move the conversation to a private chat.")
    if "urgency" in flags:
        red_flags.append("The offer uses urgency language.")
    return red_flags


def score_report(checks: List[dict], claims: Any = None) -> Tuple[int, str]:
    check_points = sum(int(check.get("risk_points", 0)) for check in checks)
    risk_score = min(check_points + claim_risk_points(claims), 100)

    return risk_score, get_level(risk_score)
# backend/tests/test_phase2.py
from backend.app.scoring import compute_risk_score, get_level, score_report


def test_scoring_function():
    score = compute_risk_score(
        domain_risk=25,
        review_risk=25,
        recruiter_risk=15,
        address_stipend_risk=15,
        company_page_risk=10,
        gemini_pattern_risk=10,
    )
    assert score == 100
    assert get_level(score) == "HIGH RISK"


def test_score_report_aggregation():
    checks = [
        {"risk_points": 25},
        {"risk_points": 25},
        {"risk_points": 0},
        {"risk_points": 5},
        {"risk_points": 10},
    ]
    score, level = score_report(checks)
    assert score == 65
    assert level == "MEDIUM RISK"