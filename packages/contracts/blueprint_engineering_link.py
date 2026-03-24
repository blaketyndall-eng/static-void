from pydantic import BaseModel, Field


class UpsertBlueprintEngineeringLinkRequest(BaseModel):
    engineering_project_id: str
    match_score: float = Field(default=0.0, ge=0, le=100)
    linkage_reason: str = ''
    is_manual_override: bool = False
