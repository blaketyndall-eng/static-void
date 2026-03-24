from pydantic import BaseModel, Field


class CreateOpportunityScanRequest(BaseModel):
    name: str
    focus: str
    source_arms: list[str] = Field(default_factory=list)
    source_queries: list[str] = Field(default_factory=list)
    notes: str = ""


class CreateOpportunityCandidateRequest(BaseModel):
    title: str
    opportunity_type: str
    summary: str = ""
    target_users: list[str] = Field(default_factory=list)
    related_apps: list[str] = Field(default_factory=list)
    related_industries: list[str] = Field(default_factory=list)
    evidence_notes: list[dict] = Field(default_factory=list)
    demand_score: float = Field(default=0.0, ge=0, le=100)
    competition_score: float = Field(default=0.0, ge=0, le=100)
    whitespace_score: float = Field(default=0.0, ge=0, le=100)
    priority_score: float = Field(default=0.0, ge=0, le=100)


class UpsertOpportunitySignalRequest(BaseModel):
    trend_signal: str = ""
    labor_signal: str = ""
    industry_signal: str = ""
    research_signal: str = ""
    source_stack: list[str] = Field(default_factory=list)
