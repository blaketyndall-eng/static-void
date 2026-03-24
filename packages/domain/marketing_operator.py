from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_marketing_run_id(prefix: str = "mkt_run") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class MarketingApprovalDecision(str, Enum):
    approve = "approve"
    iterate = "iterate"
    hold = "hold"


class MarketingDebatePacket(BaseModel):
    project_id: str
    bull_case: list[str] = Field(default_factory=list)
    bear_case: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    synthesis: str = ""


class MarketingRiskReview(BaseModel):
    project_id: str
    decision: MarketingApprovalDecision
    top_risks: list[str] = Field(default_factory=list)
    reasoning: str = ""


class MarketingOperatorRun(BaseModel):
    run_id: str = Field(default_factory=new_marketing_run_id)
    project_id: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    stages: list[dict] = Field(default_factory=list)
    debate: MarketingDebatePacket | None = None
    risk_review: MarketingRiskReview | None = None
    action_plan: list[str] = Field(default_factory=list)
