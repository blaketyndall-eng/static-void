from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_output_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ArtifactType(str, Enum):
    evidence_pack = "evidence_pack"
    comparison_brief = "comparison_brief"
    recommendation_memo = "recommendation_memo"
    research_note = "research_note"


class RecommendationStatus(str, Enum):
    draft = "draft"
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"


class EvidenceKind(str, Enum):
    quote = "quote"
    score = "score"
    document = "document"
    url = "url"
    note = "note"


class OutputBase(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ArtifactRecord(OutputBase):
    title: str
    artifact_type: ArtifactType
    linked_entity_type: str
    linked_entity_id: str
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendationRecord(OutputBase):
    title: str
    linked_entity_type: str
    linked_entity_id: str
    summary: str
    rationale: str = ""
    status: RecommendationStatus = RecommendationStatus.draft
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class EvidenceRecord(OutputBase):
    title: str
    evidence_kind: EvidenceKind
    linked_entity_type: str
    linked_entity_id: str
    source_id: str | None = None
    artifact_id: str | None = None
    detail: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
