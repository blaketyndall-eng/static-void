from pydantic import BaseModel


class CreateBrainLinkRequest(BaseModel):
    source_arm: str
    source_id: str
    target_type: str
    target_id: str
    notes: str = ""
