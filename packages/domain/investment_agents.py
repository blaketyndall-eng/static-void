from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AgentStance(str, Enum):
    bullish = "bullish"
    bearish = "bearish"
    neutral = "neutral"


class ApprovalDecision(str, Enum):
    approve = "approve"
    watch_only = "watch_only"
    reject = "reject"


class AgentInput(BaseModel):
    thesis_id: str
    ticker: str
    asset_class: str
    timeframe: str
    thesis_type: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] = Field(default_factory=dict)
    engine_output: dict[str, Any] = Field(default_factory=dict)
    portfolio_context: dict[str, Any] = Field(default_factory=dict)


class AgentOpinion(BaseModel):
    agent_name: str
    stance: AgentStance
    confidence: float = Field(ge=0, le=1)
    thesis: str
    supporting_points: list[str] = Field(default_factory=list)
    risk_points: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)


class DebatePacket(BaseModel):
    thesis_id: str
    category: str
    bullish: AgentOpinion
    bearish: AgentOpinion
    unresolved_questions: list[str] = Field(default_factory=list)
    synthesis: str = ""


class RiskReview(BaseModel):
    thesis_id: str
    decision: ApprovalDecision
    max_size_pct: float = Field(default=0.0, ge=0, le=100)
    top_risks: list[str] = Field(default_factory=list)
    overlap_flags: list[str] = Field(default_factory=list)
    liquidity_warnings: list[str] = Field(default_factory=list)
    reasoning: str = ""


class AllocationDecisionRecord(BaseModel):
    thesis_id: str
    decision: ApprovalDecision
    target_action: str
    size_guidance: str = ""
    why: str = ""


class OperatorDecisionRun(BaseModel):
    run_id: str = Field(default_factory=new_run_id)
    thesis_id: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    category: str
    stages: list[dict[str, Any]] = Field(default_factory=list)
    debate_packet: DebatePacket | None = None
    risk_review: RiskReview | None = None
    allocation_decision: AllocationDecisionRecord | None = None
