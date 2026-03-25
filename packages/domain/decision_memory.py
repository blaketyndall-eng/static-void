from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_decision_memory_workspace_id(prefix: str = 'memory') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class DecisionMemoryStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    reviewing = 'reviewing'
    archived = 'archived'


class DecisionMemoryWorkspace(BaseModel):
    id: str = Field(default_factory=new_decision_memory_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: DecisionMemoryStatus = DecisionMemoryStatus.draft
    memory_domains: list[str] = Field(default_factory=list)
    review_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class DecisionMemorySnapshot(BaseModel):
    workspace_id: str
    captured_decisions: list[str] = Field(default_factory=list)
    outcome_reviews: list[str] = Field(default_factory=list)
    regret_patterns: list[str] = Field(default_factory=list)
    reuse_candidates: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    memory_quality_score: float = Field(default=0.0, ge=0, le=100)
    calibration_score: float = Field(default=0.0, ge=0, le=100)


class DecisionMemoryReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    memory_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
