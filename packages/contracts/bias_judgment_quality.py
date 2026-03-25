from pydantic import BaseModel, Field


class CreateBiasJudgmentQualityWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    judgment_domains: list[str] = Field(default_factory=list)
    quality_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateBiasJudgmentQualityStatusRequest(BaseModel):
    status: str


class UpsertBiasJudgmentQualitySnapshotRequest(BaseModel):
    bias_checks: list[str] = Field(default_factory=list)
    calibration_rules: list[str] = Field(default_factory=list)
    dissent_prompts: list[str] = Field(default_factory=list)
    assumption_audits: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    judgment_quality_score: float = Field(default=0.0, ge=0, le=100)
    calibration_readiness_score: float = Field(default=0.0, ge=0, le=100)
