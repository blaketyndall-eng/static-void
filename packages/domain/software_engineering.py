from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_engineering_project_id(prefix: str = "eng") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class EngineeringProjectType(str, Enum):
    platform = "platform"
    application = "application"
    service = "service"
    infrastructure = "infrastructure"
    performance = "performance"
    developer_experience = "developer_experience"


class EngineeringProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"


class EngineeringWorkstream(str, Enum):
    research = "research"
    execution = "execution"
    experimentation = "experimentation"


class EngineeringProject(BaseModel):
    id: str = Field(default_factory=new_engineering_project_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    name: str
    project_type: EngineeringProjectType
    owner: str
    description: str = ""
    status: EngineeringProjectStatus = EngineeringProjectStatus.draft
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class EngineeringResearchRecord(BaseModel):
    project_id: str
    architecture_notes: list[str] = Field(default_factory=list)
    tool_recommendations: list[str] = Field(default_factory=list)
    performance_findings: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    source_notes: list[dict[str, Any]] = Field(default_factory=list)
    modernization_score: float = Field(default=0.0, ge=0, le=100)


class EngineeringExecutionRecord(BaseModel):
    project_id: str
    milestones: list[str] = Field(default_factory=list)
    active_work: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    reliability_score: float = Field(default=0.0, ge=0, le=100)
    delivery_score: float = Field(default=0.0, ge=0, le=100)


class EngineeringExperimentRecord(BaseModel):
    project_id: str
    experiments: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    adoption_candidates: list[str] = Field(default_factory=list)
    experimentation_score: float = Field(default=0.0, ge=0, le=100)
