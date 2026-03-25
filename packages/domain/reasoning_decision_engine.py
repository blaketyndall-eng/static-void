from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_reasoning_workspace_id(prefix: str = 'reason') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ReasoningDecisionEngineStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class ReasoningDecisionEngineWorkspace(BaseModel):
    id: str = Field(default_factory=new_reasoning_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: ReasoningDecisionEngineStatus = ReasoningDecisionEngineStatus.draft
    decision_domains: list[str] = Field(default_factory=list)
    reasoning_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class ReasoningDecisionEngineSnapshot(BaseModel):
    workspace_id: str
    reasoning_policies: list[str] = Field(default_factory=list)
    recommendation_strategies: list[str] = Field(default_factory=list)
    confidence_rules: list[str] = Field(default_factory=list)
    tradeoff_models: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    reasoning_quality_score: float = Field(default=0.0, ge=0, le=100)
    recommendation_confidence_score: float = Field(default=0.0, ge=0, le=100)


class ReasoningDecisionEngineReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    reasoning_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
