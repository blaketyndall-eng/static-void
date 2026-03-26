from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_image_studio_workspace_id(prefix: str = 'image') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ImageStudioStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    monitoring = 'monitoring'
    archived = 'archived'


class ImageStudioWorkspace(BaseModel):
    id: str = Field(default_factory=new_image_studio_workspace_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    owner: str
    description: str = ''
    creative_domains: list[str] = Field(default_factory=list)
    output_goals: list[str] = Field(default_factory=list)
    status: ImageStudioStatus = ImageStudioStatus.draft
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class ImageStudioSnapshot(BaseModel):
    workspace_id: str
    model_registry: list[str] = Field(default_factory=list)
    generation_modes: list[str] = Field(default_factory=list)
    prompt_recipes: list[str] = Field(default_factory=list)
    control_profiles: list[str] = Field(default_factory=list)
    edit_profiles: list[str] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)
    variant_scoring_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict[str, Any]] = Field(default_factory=list)
    creative_reliability_score: float = Field(default=0.0, ge=0, le=100)
    deployment_readiness_score: float = Field(default=0.0, ge=0, le=100)


class ImageStudioRenderJob(BaseModel):
    id: str = Field(default_factory=lambda: f"render_{uuid4().hex[:12]}")
    workspace_id: str
    mode: str
    prompt: str
    negative_prompt: str = ''
    model_name: str = ''
    width: int = 1024
    height: int = 1024
    steps: int = 20
    guidance_scale: float = 7.5
    seed: int | None = None
    control_type: str = ''
    source_asset_path: str = ''
    mask_asset_path: str = ''
    output_asset_path: str = ''
    status: str = 'queued'
    metadata: dict[str, Any] = Field(default_factory=dict)


class ImageStudioReview(BaseModel):
    workspace_id: str
    review_score: float = Field(default=0.0, ge=0, le=100)
    studio_readiness: float = Field(default=0.0, ge=0, le=100)
    top_actions: list[str] = Field(default_factory=list)
    summary: str
