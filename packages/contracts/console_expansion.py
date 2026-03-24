from pydantic import BaseModel, Field


class CreateConsoleArmWorkspaceRequest(BaseModel):
    arm_type: str
    name: str
    owner: str
    description: str = ''
    goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateConsoleArmStatusRequest(BaseModel):
    status: str


class UpsertConsoleArmSnapshotRequest(BaseModel):
    focus_areas: list[str] = Field(default_factory=list)
    active_tracks: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    maturity_score: float = Field(default=0.0, ge=0, le=100)
