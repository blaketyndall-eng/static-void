from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_engineering_run_id(prefix: str = "eng_run") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class EngineeringApprovalDecision(str, Enum):
    approve = "approve"
    iterate = "iterate"
    hold = "hold"


class EngineeringDebatePacket(BaseModel):
    project_id: str
    bull_case: list[str] = Field(default_factory=list)
    bear_case: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    synthesis: str = ""


class EngineeringRiskReview(BaseModel):
    project_id: str
    decision: EngineeringApprovalDecision
    top_risks: list[str] = Field(default_factory=list)
    reasoning: str = ""


class EngineeringOperatorRun(BaseModel):
    run_id: str = Field(default_factory=new_engineering_run_id)
    project_id: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    stages: list[dict] = Field(default_factory=list)
    debate: EngineeringDebatePacket | None = None
    risk_review: EngineeringRiskReview | None = None
    action_plan: list[str] = Field(default_factory=list)
