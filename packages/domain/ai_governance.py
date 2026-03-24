from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_ai_governance_review_id(prefix: str = 'ai_gov') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AIGovernanceStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    approved = 'approved'
    blocked = 'blocked'
    archived = 'archived'


class AIGovernanceWorkspace(BaseModel):
    id: str = Field(default_factory=new_ai_governance_review_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: AIGovernanceStatus = AIGovernanceStatus.draft
    model_scope: list[str] = Field(default_factory=list)
    evaluation_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class AIGovernanceSnapshot(BaseModel):
    workspace_id: str
    benchmark_tracks: list[str] = Field(default_factory=list)
    policy_checks: list[str] = Field(default_factory=list)
    monitoring_checks: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    governance_score: float = Field(default=0.0, ge=0, le=100)


class AIGovernanceReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    approval_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
