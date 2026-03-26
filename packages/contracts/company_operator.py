from pydantic import BaseModel, Field


class CreateCompanyOperatorWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    company_names: list[str] = Field(default_factory=list)
    operating_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateCompanyOperatorStatusRequest(BaseModel):
    status: str


class UpsertCompanyOperatorSnapshotRequest(BaseModel):
    company_goals: list[str] = Field(default_factory=list)
    operating_cadences: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
    initiatives: list[str] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    decision_execution_links: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    operating_health_score: float = Field(default=0.0, ge=0, le=100)
    execution_alignment_score: float = Field(default=0.0, ge=0, le=100)
