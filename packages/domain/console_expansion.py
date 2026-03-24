from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_console_arm_id(prefix: str = 'arm') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ConsoleArmType(str, Enum):
    ai_governance = 'ai_governance'
    signals_forecasting = 'signals_forecasting'
    research_lab = 'research_lab'
    agent_studio = 'agent_studio'
    vertical_packs = 'vertical_packs'
    decision_memory = 'decision_memory'
    integrations_automation = 'integrations_automation'
    data_source_intelligence = 'data_source_intelligence'


class ConsoleArmStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    paused = 'paused'
    archived = 'archived'


class ConsoleArmWorkspace(BaseModel):
    id: str = Field(default_factory=new_console_arm_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    arm_type: ConsoleArmType
    name: str
    owner: str
    description: str = ''
    status: ConsoleArmStatus = ConsoleArmStatus.draft
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class ConsoleArmSnapshot(BaseModel):
    workspace_id: str
    focus_areas: list[str] = Field(default_factory=list)
    active_tracks: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    maturity_score: float = Field(default=0.0, ge=0, le=100)


class ConsoleArmReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    readiness_score: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
