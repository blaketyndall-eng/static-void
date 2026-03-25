from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_feedback_workspace_id(prefix: str = 'feedback') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class FeedbackOutcomeScoringStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class FeedbackOutcomeScoringWorkspace(BaseModel):
    id: str = Field(default_factory=new_feedback_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    outcome_domains: list[str] = Field(default_factory=list)
    scoring_goals: list[str] = Field(default_factory=list)
    status: FeedbackOutcomeScoringStatus = FeedbackOutcomeScoringStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class FeedbackOutcomeScoringSnapshot(BaseModel):
    workspace_id: str
    outcome_reviews: list[str] = Field(default_factory=list)
    prediction_checks: list[str] = Field(default_factory=list)
    usefulness_scores: list[str] = Field(default_factory=list)
    regret_signals: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    outcome_quality_score: float = Field(default=0.0, ge=0, le=100)
    feedback_readiness_score: float = Field(default=0.0, ge=0, le=100)


class FeedbackOutcomeScoringReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    feedback_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
