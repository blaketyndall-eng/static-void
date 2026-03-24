from pydantic import BaseModel, Field


class CreateAppRequest(BaseModel):
    name: str
    app_type: str
    owner: str
    description: str = ""
    version: str = "0.1.0"
    runtime_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    linked_brain_modules: list[str] = Field(default_factory=list)


class UpdateAppStatusRequest(BaseModel):
    status: str


class UpdateDeploymentStateRequest(BaseModel):
    deployment_state: str


class CreateAppRunRequest(BaseModel):
    output_summary: str = ""
    error_summary: str = ""


class CreateAppFeedbackRequest(BaseModel):
    category: str
    severity: str = "info"
    message: str
