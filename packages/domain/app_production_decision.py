from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_app_production_decision_id(prefix: str = 'app_prod') -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AppProductionDecisionState(str, Enum):
    ready = 'ready'
    iterate = 'iterate'
    hold = 'hold'


class AppProductionDecision(BaseModel):
    id: str = Field(default_factory=new_app_production_decision_id)
    created_at: datetime = Field(default_factory=utc_now)
    blueprint_id: str
    decision: AppProductionDecisionState
    rationale: str = ''
    action_items: list[str] = Field(default_factory=list)
    advisory_score: float = Field(default=0.0, ge=0, le=100)
