from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class EntityStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    archived = "archived"


class BaseEntity(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class SourceType(str, Enum):
    api = "api"
    website = "website"
    document = "document"
    dataset = "dataset"
    manual = "manual"


class SourceRecord(BaseEntity):
    name: str
    source_type: SourceType
    trust_score: float = Field(default=0.5, ge=0, le=1)
    freshness_label: str = "unknown"
    owner: str | None = None
    notes: str = ""
    tags: list[str] = Field(default_factory=list)


class OpportunityStage(str, Enum):
    new = "new"
    qualified = "qualified"
    incubating = "incubating"
    rejected = "rejected"
    shipped = "shipped"


class OpportunityRecord(BaseEntity):
    title: str
    summary: str
    stage: OpportunityStage = OpportunityStage.new
    score: float | None = Field(default=None, ge=0, le=100)
    source_ids: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)


class EventCategory(str, Enum):
    source = "source"
    opportunity = "opportunity"
    evaluation = "evaluation"
    recommendation = "recommendation"
    experiment = "experiment"
    system = "system"


class EventRecord(BaseEntity):
    category: EventCategory
    event_type: str
    entity_type: str
    entity_id: str
    actor: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class EvaluationStatus(str, Enum):
    scoped = "scoped"
    evidence_gathering = "evidence_gathering"
    scoring = "scoring"
    review = "review"
    complete = "complete"


class EvaluationRecord(BaseEntity):
    title: str
    status: EvaluationStatus = EvaluationStatus.scoped
    decision_owner: str | None = None
    criteria: list[dict[str, Any]] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    recommendation_summary: str = ""
