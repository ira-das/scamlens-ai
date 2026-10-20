# backend/app/main.py
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ScamLens AI",
    version="0.1.0",
    description="Phase 1 skeleton for ScamLens AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "ScamLens AI"}


from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.gemini_client import extract_claims_regex
from backend.app.models import TrustReport
from backend.app.checks.verification_checks import run_all_checks
from backend.app.scoring import score_report

app = FastAPI(
    title="ScamLens AI",
    version="0.1.0",
    description="ScamLens AI backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "ScamLens AI"}


class VerifyRequest(BaseModel):
    text: str


@app.post("/api/verify")
async def verify_offer(payload: VerifyRequest) -> dict:
    claims = extract_claims_regex(payload.text)
    checks = await run_all_checks(claims.model_dump())

    risk_score, level = score_report(
        [check.model_dump() for check in checks]
    )

    red_flags = []
    for check in checks:
        if check.status in {"bad", "warn"}:
            red_flags.append(check.summary)

    report = {
        "claims": claims.model_dump(),
        "checks": [check.model_dump() for check in checks],
        "risk_score": risk_score,
        "level": level,
        "red_flags": red_flags,
        "summary": "Offer reviewed with mock checks.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return report