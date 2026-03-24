from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_event_id(prefix: str = "evt") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class SystemEventType(str, Enum):
    app_created = "app_created"
    app_updated = "app_updated"
    blueprint_created = "blueprint_created"
    marketing_project_created = "marketing_project_created"
    investment_thesis_created = "investment_thesis_created"
    opportunity_scan_created = "opportunity_scan_created"
    opportunity_candidate_created = "opportunity_candidate_created"
    brain_link_created = "brain_link_created"
    operator_action = "operator_action"


class SystemEventRecord(BaseModel):
    id: str = Field(default_factory=new_event_id)
    created_at: datetime = Field(default_factory=utc_now)
    event_type: SystemEventType
    source_arm: str
    source_id: str
    summary: str
    metadata: dict = Field(default_factory=dict)
