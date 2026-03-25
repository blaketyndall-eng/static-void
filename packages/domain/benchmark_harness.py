from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_benchmark_workspace_id(prefix: str = 'bench') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class BenchmarkHarnessStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class BenchmarkHarnessWorkspace(BaseModel):
    id: str = Field(default_factory=new_benchmark_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    status: BenchmarkHarnessStatus = BenchmarkHarnessStatus.draft
    benchmark_domains: list[str] = Field(default_factory=list)
    benchmark_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class BenchmarkHarnessSnapshot(BaseModel):
    workspace_id: str
    benchmark_suites: list[str] = Field(default_factory=list)
    replay_datasets: list[str] = Field(default_factory=list)
    challenger_models: list[str] = Field(default_factory=list)
    rollback_rules: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    benchmark_quality_score: float = Field(default=0.0, ge=0, le=100)
    harness_readiness_score: float = Field(default=0.0, ge=0, le=100)


class BenchmarkHarnessReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    benchmark_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
