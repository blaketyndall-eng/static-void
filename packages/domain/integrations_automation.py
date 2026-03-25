from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_integration_workspace_id(prefix: str = 'integration') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class IntegrationsAutomationStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class IntegrationsAutomationWorkspace(BaseModel):
    id: str = Field(default_factory=new_integration_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: IntegrationsAutomationStatus = IntegrationsAutomationStatus.draft
    integration_targets: list[str] = Field(default_factory=list)
    automation_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class IntegrationsAutomationSnapshot(BaseModel):
    workspace_id: str
    integration_health_checks: list[str] = Field(default_factory=list)
    automation_workflows: list[str] = Field(default_factory=list)
    webhook_endpoints: list[str] = Field(default_factory=list)
    freshness_alerts: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    integration_health_score: float = Field(default=0.0, ge=0, le=100)
    automation_reliability_score: float = Field(default=0.0, ge=0, le=100)


class IntegrationsAutomationReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    automation_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
