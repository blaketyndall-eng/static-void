from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_ingestion_workspace_id(prefix: str = 'ingest') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class IngestionDataAcquisitionStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class IngestionDataAcquisitionWorkspace(BaseModel):
    id: str = Field(default_factory=new_ingestion_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: IngestionDataAcquisitionStatus = IngestionDataAcquisitionStatus.draft
    source_targets: list[str] = Field(default_factory=list)
    ingestion_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class IngestionDataAcquisitionSnapshot(BaseModel):
    workspace_id: str
    connectors: list[str] = Field(default_factory=list)
    sync_jobs: list[str] = Field(default_factory=list)
    normalization_pipelines: list[str] = Field(default_factory=list)
    freshness_windows: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    ingestion_health_score: float = Field(default=0.0, ge=0, le=100)
    normalization_readiness_score: float = Field(default=0.0, ge=0, le=100)


class IngestionDataAcquisitionReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    ingestion_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
