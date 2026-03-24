from pydantic import BaseModel, Field


class CreateSystemEventRequest(BaseModel):
    event_type: str
    source_arm: str
    source_id: str
    summary: str
    metadata: dict = Field(default_factory=dict)
