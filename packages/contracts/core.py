from typing import Any

from pydantic import BaseModel, Field


class CreateSourceRequest(BaseModel):
    name: str
    source_type: str
    trust_score: float = Field(default=0.5, ge=0, le=1)
    freshness_label: str = "unknown"
    owner: str | None = None
    notes: str = ""
    tags: list[str] = Field(default_factory=list)


class CreateOpportunityRequest(BaseModel):
    title: str
    summary: str
    source_ids: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    score: float | None = Field(default=None, ge=0, le=100)


class CreateEvaluationRequest(BaseModel):
    title: str
    decision_owner: str | None = None
    criteria: list[dict[str, Any]] = Field(default_factory=list)


class AttachEvidenceRequest(BaseModel):
    evidence_id: str
