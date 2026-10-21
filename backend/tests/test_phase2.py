from fastapi.testclient import TestClient

from backend.app import tinyfish_client
from backend.app.gemini_client import extract_claims_regex
from backend.app.main import app
from backend.app.scoring import compute_risk_score, get_level, score_report

client = TestClient(app)

FAKE_TEXT = """
Urgent internship opening! We need a ₹5000 security deposit before onboarding.
Email hr@internship-portal.xyz and contact me on WhatsApp immediately.
Regards, Priya Sharma
No interview needed. Submit Aadhaar and OTP.
"""

GENUINE_TEXT = """
TCS internship opportunity in software development.
Official domain: tcs.com
Stipend ₹18000 per month.
Location: Bengaluru.
No fee required.
"""


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


def test_claim_validation():
    claims = extract_claims_regex(FAKE_TEXT)
    assert claims.domain == "internship-portal.xyz"
    assert claims.recruiter_name == "Priya Sharma"
    assert "private_chat" in claims.scam_wording_flags
    assert claims.fee_demanded == 5000


def test_fake_offer_is_high_risk(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", True)

    response = client.post("/api/verify", json={"text": FAKE_TEXT})

    assert response.status_code == 200
    report = response.json()
    assert report["risk_score"] >= 70
    assert report["level"] == "HIGH RISK"


def test_genuine_offer_is_low_risk(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", True)

    response = client.post("/api/verify", json={"text": GENUINE_TEXT})

    assert response.status_code == 200
    report = response.json()
    assert report["claims"]["fee_demanded"] == 0
    assert report["claims"]["domain"] == "tcs.com"
    assert report["claims"]["company"] == "TCS"
    assert report["level"] == "LOW RISK"
    assert not any("fee" in flag.lower() for flag in report["red_flags"])


def test_unknown_claims_skip_company_search(monkeypatch):
    monkeypatch.setattr(tinyfish_client, "USE_MOCKS", True)

    response = client.post("/api/verify", json={"text": "A software internship opportunity."})

    assert response.status_code == 200
    checks = response.json()["checks"]
    company_check = next(check for check in checks if check["name"] == "Company & Careers Page Check")
    assert company_check["status"] == "error"
    assert company_check["risk_points"] == 0
    assert company_check["max_points"] == 10
    assert "Example Corp" not in company_check["summary"]