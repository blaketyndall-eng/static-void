from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_agent_workforce_workspace_id(prefix: str = 'agent') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AgentWorkforceStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class AgentWorkforceWorkspace(BaseModel):
    id: str = Field(default_factory=new_agent_workforce_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    agent_roles: list[str] = Field(default_factory=list)
    workforce_goals: list[str] = Field(default_factory=list)
    status: AgentWorkforceStatus = AgentWorkforceStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class AgentWorkforceSnapshot(BaseModel):
    workspace_id: str
    permissions: list[str] = Field(default_factory=list)
    budgets: list[str] = Field(default_factory=list)
    routing_policies: list[str] = Field(default_factory=list)
    task_queues: list[str] = Field(default_factory=list)
    hitl_checkpoints: list[str] = Field(default_factory=list)
    tool_access: list[str] = Field(default_factory=list)
    escalation_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    workforce_reliability_score: float = Field(default=0.0, ge=0, le=100)
    governance_readiness_score: float = Field(default=0.0, ge=0, le=100)


class AgentWorkforceReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    workforce_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
