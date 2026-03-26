from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_operator_team_workspace_id(prefix: str = 'opteam') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class OperatorTeamStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class OperatorTeamWorkspace(BaseModel):
    id: str = Field(default_factory=new_operator_team_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    team_roles: list[str] = Field(default_factory=list)
    team_goals: list[str] = Field(default_factory=list)
    status: OperatorTeamStatus = OperatorTeamStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class OperatorTeamSnapshot(BaseModel):
    workspace_id: str
    access_rules: list[str] = Field(default_factory=list)
    credit_limits: list[str] = Field(default_factory=list)
    routing_rules: list[str] = Field(default_factory=list)
    work_queues: list[str] = Field(default_factory=list)
    human_review_points: list[str] = Field(default_factory=list)
    tool_links: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    reliability_score: float = Field(default=0.0, ge=0, le=100)
    readiness_score: float = Field(default=0.0, ge=0, le=100)


class OperatorTeamReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    team_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
