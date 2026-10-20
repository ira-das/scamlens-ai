from __future__ import annotations

from typing import List, Tuple

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
    (59, "MEDIUM RISK"),
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
    if score <= 59:
        return "MEDIUM RISK"
    return "HIGH RISK"


def score_report(checks: List[dict]) -> Tuple[int, str]:
    risk_score = 0
    for check in checks:
        risk_score += int(check.get("risk_points", 0))

    # Cap to the brief requirement
    risk_score = min(risk_score, 100)
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