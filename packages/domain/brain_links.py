from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_brain_link_id(prefix: str = "brain_link") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class BrainLinkType(str, Enum):
    app_to_module = "app_to_module"
    marketing_to_module = "marketing_to_module"
    investment_to_module = "investment_to_module"
    cross_arm_reference = "cross_arm_reference"


class BrainLinkRecord(BaseModel):
    id: str = Field(default_factory=new_brain_link_id)
    created_at: datetime = Field(default_factory=utc_now)
    source_arm: str
    source_id: str
    target_type: BrainLinkType
    target_id: str
    notes: str = ""


class BrainModuleSummary(BaseModel):
    module_name: str
    linked_count: int = 0
    source_arms: list[str] = Field(default_factory=list)
