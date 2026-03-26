from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_company_operator_workspace_id(prefix: str = 'company') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class CompanyOperatorStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class CompanyOperatorWorkspace(BaseModel):
    id: str = Field(default_factory=new_company_operator_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    company_names: list[str] = Field(default_factory=list)
    operating_goals: list[str] = Field(default_factory=list)
    status: CompanyOperatorStatus = CompanyOperatorStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class CompanyOperatorSnapshot(BaseModel):
    workspace_id: str
    company_goals: list[str] = Field(default_factory=list)
    operating_cadences: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
    initiatives: list[str] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    decision_execution_links: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    operating_health_score: float = Field(default=0.0, ge=0, le=100)
    execution_alignment_score: float = Field(default=0.0, ge=0, le=100)


class CompanyOperatorReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    operator_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
