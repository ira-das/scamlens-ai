from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.checks.verification_checks import run_all_checks
from backend.app.gemini_client import extract_claims_regex
from backend.app.scoring import claim_red_flags, score_report

DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


class VerifyRequest(BaseModel):
    text: str


def get_allowed_origins() -> list[str]:
    """Read comma-separated CORS origins, falling back to local development URLs."""
    configured = os.getenv("ALLOWED_ORIGINS")
    if configured is None:
        return list(DEFAULT_ALLOWED_ORIGINS)

    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    return origins or list(DEFAULT_ALLOWED_ORIGINS)


def create_app() -> FastAPI:
    """Create the ScamLens API with CORS configured from the environment."""
    allowed_origins = get_allowed_origins()
    application = FastAPI(
        title="ScamLens AI",
        version="0.1.0",
        description="ScamLens AI backend",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials="*" not in allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "ScamLens AI"}

    @application.post("/api/verify")
    async def verify_offer(payload: VerifyRequest) -> dict:
        claims = extract_claims_regex(payload.text)
        claim_data = claims.model_dump()
        checks = await run_all_checks(claim_data)
        check_data = [check.model_dump() for check in checks]
        risk_score, level = score_report(check_data, claims=claim_data)

        red_flags = claim_red_flags(claim_data)
        red_flags.extend(
            check.summary for check in checks if check.status in {"bad", "warn"}
        )

        return {
            "claims": claim_data,
            "checks": check_data,
            "risk_score": risk_score,
            "level": level,
            "red_flags": red_flags,
            "summary": "Offer reviewed with mock checks.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    return application


app = create_app()