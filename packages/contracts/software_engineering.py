from pydantic import BaseModel, Field


class CreateEngineeringProjectRequest(BaseModel):
    name: str
    project_type: str
    owner: str
    description: str = ""
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateEngineeringProjectStatusRequest(BaseModel):
    status: str


class UpsertEngineeringResearchRequest(BaseModel):
    architecture_notes: list[str] = Field(default_factory=list)
    tool_recommendations: list[str] = Field(default_factory=list)
    performance_findings: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    source_notes: list[dict] = Field(default_factory=list)
    modernization_score: float = Field(default=0.0, ge=0, le=100)


class UpsertEngineeringExecutionRequest(BaseModel):
    milestones: list[str] = Field(default_factory=list)
    active_work: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    reliability_score: float = Field(default=0.0, ge=0, le=100)
    delivery_score: float = Field(default=0.0, ge=0, le=100)


class UpsertEngineeringExperimentRequest(BaseModel):
    experiments: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    adoption_candidates: list[str] = Field(default_factory=list)
    experimentation_score: float = Field(default=0.0, ge=0, le=100)
