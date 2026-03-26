from pydantic import BaseModel, Field


class CreateImageStudioWorkspaceRequest(BaseModel):
    name: str
    owner: str
    description: str = ''
    creative_domains: list[str] = Field(default_factory=list)
    output_goals: list[str] = Field(default_factory=list)
    linked_apps: list[str] = Field(default_factory=list)
    linked_modules: list[str] = Field(default_factory=list)


class UpdateImageStudioStatusRequest(BaseModel):
    status: str


class UpsertImageStudioSnapshotRequest(BaseModel):
    model_registry: list[str] = Field(default_factory=list)
    generation_modes: list[str] = Field(default_factory=list)
    prompt_recipes: list[str] = Field(default_factory=list)
    control_profiles: list[str] = Field(default_factory=list)
    edit_profiles: list[str] = Field(default_factory=list)
    artifact_paths: list[str] = Field(default_factory=list)
    variant_scoring_rules: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    notes: list[dict] = Field(default_factory=list)
    creative_reliability_score: float = Field(default=0.0, ge=0, le=100)
    deployment_readiness_score: float = Field(default=0.0, ge=0, le=100)


class CreateImageStudioRenderJobRequest(BaseModel):
    mode: str
    prompt: str
    negative_prompt: str = ''
    model_name: str = ''
    width: int = 1024
    height: int = 1024
    steps: int = 20
    guidance_scale: float = 7.5
    seed: int | None = None
    control_type: str = ''
    source_asset_path: str = ''
    mask_asset_path: str = ''
    metadata: dict = Field(default_factory=dict)
