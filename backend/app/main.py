from __future__ import annotations

import os
import logging
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPOSITORY_ROOT / ".env", override=False)

from backend.app import tinyfish_client
from backend.app.checks.verification_checks import run_all_checks
from backend.app.gemini_client import extract_claims_regex
from backend.app.scoring import claim_red_flags, score_report

DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)
logger = logging.getLogger("uvicorn.error")


class VerifyRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, text: str) -> str:
        if len(text) < 10:
            raise ValueError("Offer text must contain at least 10 characters.")
        if len(text) > 5000:
            raise ValueError("Offer text must contain no more than 5000 characters.")
        return text


class InMemoryRateLimiter:
    """Track request timestamps per client IP for a short sliding window."""

    def __init__(self, limit: int = 20, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, Deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow_request(self, client_ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self.lock:
            timestamps = self.requests[client_ip]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return False
            timestamps.append(now)
            return True


def get_allowed_origins() -> list[str]:
    """Read comma-separated CORS origins, falling back to local development URLs."""
    configured = os.getenv("ALLOWED_ORIGINS")
    if configured is None:
        return list(DEFAULT_ALLOWED_ORIGINS)

    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    return origins or list(DEFAULT_ALLOWED_ORIGINS)


def get_allowed_origin_regex() -> str | None:
    """Read the optional regular expression used for preview deployments."""
    configured = os.getenv("ALLOWED_ORIGIN_REGEX", "").strip()
    return configured or None


def resolve_runtime_mode() -> str:
    """Resolve mock/live mode without exposing whether a key is present in logs."""
    use_mocks_value = os.getenv("USE_MOCKS", "true").strip().lower()
    live_requested = use_mocks_value in {"false", "0", "no"}
    api_key_is_set = bool(os.getenv("TINYFISH_API_KEY", "").strip())
    if live_requested and not api_key_is_set:
        logger.warning("Live mode requested but TINYFISH_API_KEY is not set; using mocks")
        return "mock"
    return "live" if live_requested else "mock"


def create_app() -> FastAPI:
    """Create the ScamLens API with CORS configured from the environment."""
    allowed_origins = get_allowed_origins()
    allowed_origin_regex = get_allowed_origin_regex()
    mode = resolve_runtime_mode()
    disable_agent_checks = os.getenv("DISABLE_AGENT_CHECKS", "false").strip().lower() in {
        "true",
        "1",
        "yes",
    }
    tinyfish_client.configure_runtime(mode == "mock", disable_agent_checks)
    logger.info("ScamLens mode: %s", mode.upper())
    rate_limiter = InMemoryRateLimiter()
    application = FastAPI(
        title="ScamLens AI",
        version="0.1.0",
        description="ScamLens AI backend",
    )
    application.state.mode = mode
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=allowed_origin_regex,
        allow_credentials="*" not in allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "mode": mode}

    @application.post("/api/verify")
    async def verify_offer(payload: VerifyRequest, request: Request) -> dict:
        client_ip = request.client.host if request.client else "unknown"
        if not rate_limiter.allow_request(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many verification requests. Please wait a minute and try again.",
            )

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
            "summary": (
                "Offer reviewed with live TinyFish checks."
                if mode == "live"
                else "Offer reviewed with mock checks."
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    return application


app = create_app()