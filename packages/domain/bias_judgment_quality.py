from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_bias_workspace_id(prefix: str = 'bias') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class BiasJudgmentQualityStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class BiasJudgmentQualityWorkspace(BaseModel):
    id: str = Field(default_factory=new_bias_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: BiasJudgmentQualityStatus = BiasJudgmentQualityStatus.draft
    judgment_domains: list[str] = Field(default_factory=list)
    quality_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class BiasJudgmentQualitySnapshot(BaseModel):
    workspace_id: str
    bias_checks: list[str] = Field(default_factory=list)
    calibration_rules: list[str] = Field(default_factory=list)
    dissent_prompts: list[str] = Field(default_factory=list)
    assumption_audits: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    judgment_quality_score: float = Field(default=0.0, ge=0, le=100)
    calibration_readiness_score: float = Field(default=0.0, ge=0, le=100)


class BiasJudgmentQualityReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    judgment_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
