from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_action_workspace_id(prefix: str = 'action') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ActionWorkflowExecutionStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class ActionWorkflowExecutionWorkspace(BaseModel):
    id: str = Field(default_factory=new_action_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    execution_domains: list[str] = Field(default_factory=list)
    workflow_goals: list[str] = Field(default_factory=list)
    status: ActionWorkflowExecutionStatus = ActionWorkflowExecutionStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class ActionWorkflowExecutionSnapshot(BaseModel):
    workspace_id: str
    workflow_templates: list[str] = Field(default_factory=list)
    approval_checkpoints: list[str] = Field(default_factory=list)
    connector_actions: list[str] = Field(default_factory=list)
    execution_logs: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    execution_reliability_score: float = Field(default=0.0, ge=0, le=100)
    approval_readiness_score: float = Field(default=0.0, ge=0, le=100)


class ActionWorkflowExecutionReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    execution_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
