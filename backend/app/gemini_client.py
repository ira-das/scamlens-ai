from __future__ import annotations

import os
import re
from typing import Any, Dict

from backend.app.models import ClaimExtraction

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
USE_MOCKS = os.getenv("USE_MOCKS", "true").lower() == "true"

AMOUNT = re.compile(r"(?:\u20b9|rs\.?|inr)\s*([\d,]+)", re.IGNORECASE)
FEE_WORDS = re.compile(
    r"\b(fee|fees|deposit|charges?|registration|kit|training|security)\b",
    re.IGNORECASE,
)


def extract_fee(text: str) -> int:
    for line in text.splitlines():
        for m in AMOUNT.finditer(line):
            context = line[max(0, m.start() - 30): m.start()] + " " + line[m.end(): m.end() + 30]
            if FEE_WORDS.search(context):
                return int(m.group(1).replace(",", ""))
            # stipend/salary amounts fall through and are ignored
    return 0


def extract_claims_regex(text: str) -> ClaimExtraction:
    lowered = text.lower()

    company_match = re.search(
        r"for\s+([A-Z][A-Za-z0-9&.\- ]+?)(?:\s+intern|\s+job|\s+role)",
        text,
        flags=re.I,
    )
    company = company_match.group(1).strip() if company_match else None
    if not company and re.search(r"(?im)^\s*TCS\b", text):
        company = "TCS"

    email_domain_match = re.search(r"@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)", text)
    official_domain_match = re.search(
        r"domain[:\s]+([A-Za-z0-9.-]+\.[a-z]{2,})",
        text,
        flags=re.I,
    )
    domain_match = email_domain_match or official_domain_match
    domain = domain_match.group(1).lower() if domain_match else None
    if not company and domain == "tcs.com":
        company = "TCS"

    recruiter_name = None
    recruiter_match = re.search(
        r"(?:\b(?:i am|this is|regards)\b[ \t]*[,:\-]?[ \t]+)([A-Z][A-Za-z]+(?:[ \t]+[A-Z][A-Za-z]+){1,2})(?=[ \t]*(?:\n|,|\d|$))",
        text,
        flags=re.I,)
    if recruiter_match:
        recruiter_name = recruiter_match.group(1).strip()

    

    stipend_match = re.search(r"₹\\s?(\\d{3,6})(?:\\s*(?:per|/|monthly|month))?", text, flags=re.I)
    stipend = int(stipend_match.group(1)) if stipend_match else None

    fee_demanded = extract_fee(text)
    
    upi_match = re.search(r"(upi|phonepe|paytm|googlepay)[^\\w]*([A-Za-z0-9@\\-_.]+)", text, flags=re.I)
    upi_id = upi_match.group(2).strip() if upi_match else None

    address_match = re.search(r"(?:address|location)[^\\n:]*:?(.*)", text, flags=re.I)
    address = address_match.group(1).strip() if address_match else None

    flags = []
    scam_patterns = {
        "urgency": r"urgent|immediately|today|ASAP|within\s+24\s+hours",
        "private_chat": r"whatsapp|telegram|dm|direct message",
        "no_interview": r"no interview|no test|no screening",
        "aadhaar": r"aadhaar|bank details|otp|upi|account details",
    }

    for label, pattern in scam_patterns.items():
        if re.search(pattern, text, flags=re.I):
            flags.append(label)

    return ClaimExtraction(
        company=company,
        domain=domain,
        recruiter_name=recruiter_name,
        recruiter_email=None,
        stipend=stipend,
        fee_demanded=fee_demanded,
        upi_id=upi_id,
        address=address,
        scam_wording_flags=flags,
    )