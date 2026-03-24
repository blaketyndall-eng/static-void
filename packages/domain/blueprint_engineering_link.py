from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_blueprint_link_id(prefix: str = 'bp_eng') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class BlueprintEngineeringLink(BaseModel):
    id: str = Field(default_factory=new_blueprint_link_id)
    created_at: datetime = Field(default_factory=utc_now)
    blueprint_id: str
    engineering_project_id: str
    match_score: float = Field(default=0.0, ge=0, le=100)
    linkage_reason: str = ''
    is_manual_override: bool = False
