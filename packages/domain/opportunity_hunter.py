from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_opportunity_scan_id(prefix: str = "opp_scan") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def new_opportunity_id(prefix: str = "opp") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class OpportunityType(str, Enum):
    active_app_expansion = "active_app_expansion"
    related_industry = "related_industry"
    niche = "niche"
    underserved_industry = "underserved_industry"
    workflow_gap = "workflow_gap"
    data_product = "data_product"
    agency_service = "agency_service"
    enablement_tool = "enablement_tool"


class OpportunityStatus(str, Enum):
    detected = "detected"
    shortlisted = "shortlisted"
    researching = "researching"
    validated = "validated"
    archived = "archived"


class OpportunityScan(BaseModel):
    id: str = Field(default_factory=new_opportunity_scan_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    focus: str
    source_arms: list[str] = Field(default_factory=list)
    source_queries: list[str] = Field(default_factory=list)
    notes: str = ""


class OpportunityCandidate(BaseModel):
    id: str = Field(default_factory=new_opportunity_id)
    scan_id: str
    title: str
    opportunity_type: OpportunityType
    status: OpportunityStatus = OpportunityStatus.detected
    summary: str = ""
    target_users: list[str] = Field(default_factory=list)
    related_apps: list[str] = Field(default_factory=list)
    related_industries: list[str] = Field(default_factory=list)
    evidence_notes: list[dict[str, Any]] = Field(default_factory=list)
    demand_score: float = Field(default=0.0, ge=0, le=100)
    competition_score: float = Field(default=0.0, ge=0, le=100)
    whitespace_score: float = Field(default=0.0, ge=0, le=100)
    priority_score: float = Field(default=0.0, ge=0, le=100)


class OpportunityMarketSignal(BaseModel):
    candidate_id: str
    trend_signal: str = ""
    labor_signal: str = ""
    industry_signal: str = ""
    research_signal: str = ""
    source_stack: list[str] = Field(default_factory=list)


class OpportunityLearningSnapshot(BaseModel):
    scan_id: str
    total_candidates: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    top_patterns: list[str] = Field(default_factory=list)
    average_priority_score: float = 0.0
