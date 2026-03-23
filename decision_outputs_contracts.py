from typing import Any

from pydantic import BaseModel, Field


class CreateArtifactRequest(BaseModel):
    title: str
    artifact_type: str
    linked_entity_type: str
    linked_entity_id: str
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateRecommendationRequest(BaseModel):
    title: str
    linked_entity_type: str
    linked_entity_id: str
    summary: str
    rationale: str = ""
    status: str = "draft"
    artifact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class CreateEvidenceRequest(BaseModel):
    title: str
    evidence_kind: str
    linked_entity_type: str
    linked_entity_id: str
    source_id: str | None = None
    artifact_id: str | None = None
    detail: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
