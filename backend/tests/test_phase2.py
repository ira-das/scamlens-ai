# backend/tests/test_phase2.py
from backend.app.gemini_client import extract_claims_regex
from backend.app.scoring import score_report

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

def test_claim_validation():
    claims = extract_claims_regex(FAKE_TEXT)
    assert claims.domain is not None
    assert claims.recruiter_name == "Priya Sharma"
    assert "private_chat" in claims.scam_wording_flags
    assert claims.fee_demanded > 0

def test_mock_pipeline_high_risk_for_fake_offer():
    claims = extract_claims_regex(FAKE_TEXT)
    checks = [
        {"risk_points": 25},
        {"risk_points": 25},
        {"risk_points": 15},
        {"risk_points": 25},
        {"risk_points": 15},
    ]
    score, level = score_report(checks)
    assert score >= 60
    assert level == "HIGH RISK"

def test_mock_pipeline_low_risk_for_genuine_offer():
    claims = extract_claims_regex(GENUINE_TEXT)
    checks = [
        {"risk_points": 0},
        {"risk_points": 0},
        {"risk_points": 0},
        {"risk_points": 0},
        {"risk_points": 0},
    ]
    score, level = score_report(checks)
    assert score <= 29
    assert level == "LOW RISK"