from pydantic import BaseModel, Field


class UpsertAppProductionDecisionRequest(BaseModel):
    decision: str
    rationale: str = ''
    action_items: list[str] = Field(default_factory=list)
    advisory_score: float = Field(default=0.0, ge=0, le=100)
