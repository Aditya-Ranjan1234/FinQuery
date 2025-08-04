"""Centralised Pydantic models used across the project."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Clause(BaseModel):
    """A chunk of source text that may be referenced in a decision."""

    id: str = Field(..., description="Deterministic identifier (e.g. UUID or <file>:<page>:<idx>).")
    text: str = Field(..., description="Exact text of the clause or chunk.")
    source: str = Field(..., description="Original document file name or URI.")


class Query(BaseModel):
    """Structured representation extracted from the user's natural-language query."""

    age: Optional[int] = None
    gender: Optional[str] = None  # "M" | "F" | None
    procedure: Optional[str] = None
    location: Optional[str] = None
    policy_age_months: Optional[int] = Field(None, alias="policy_months")

    raw: str = Field(..., description="Original query text.")
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    # Normalise gender
    @validator("gender", pre=True)
    def _normalise_gender(cls, v: str | None):  # noqa: N805
        if not v:
            return v
        v = v.lower()
        if v in {"m", "male"}:
            return "M"
        if v in {"f", "female"}:
            return "F"
        return v


class DecisionResponse(BaseModel):
    """Final system response returned to downstream consumer."""

    decision: str = Field(..., description="Approved / Rejected / Needs review …")
    amount: Optional[float] = Field(None, description="Payout amount if applicable.")
    justification: str = Field(..., description="Human-readable explanation of the decision.")
    clauses: List[Clause] = Field(..., description="Clauses used for justification.")

    def to_json(self):  # pragma: no cover
        """Wrapper to serialise as JSON string with UTF-8 characters preserved."""
        return self.model_dump_json(ensure_ascii=False)
