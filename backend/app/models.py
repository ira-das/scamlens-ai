from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ClaimExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: Optional[str] = None
    domain: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    stipend: Optional[int] = None
    fee_demanded: Optional[int] = None
    upi_id: Optional[str] = None
    address: Optional[str] = None
    scam_wording_flags: List[str] = Field(default_factory=list)

    @field_validator("scam_wording_flags")
    @classmethod
    def validate_flags(cls, value):
        if value is None:
            return []
        return value


class EvidenceItem(BaseModel):
    label: str
    url: str
    retrieved_at: str


class CheckResult(BaseModel):
    name: str
    tool_used: str
    status: Literal["ok", "warn", "bad", "error"]
    summary: str
    risk_points: int = 0
    max_points: int = 0
    evidence: List[EvidenceItem] = Field(default_factory=list)


class TrustReport(BaseModel):
    claims: ClaimExtraction
    checks: List[CheckResult]
    risk_score: int
    level: str
    red_flags: List[str]
    summary: str
    generated_at: str