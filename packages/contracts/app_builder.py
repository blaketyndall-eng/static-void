from pydantic import BaseModel, Field


class CreateAppBlueprintRequest(BaseModel):
    name: str
    app_type: str
    description: str = ""
    target_users: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)
    required_engines: list[str] = Field(default_factory=list)
    primary_views: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    notes: str = ""


class GenerateScaffoldPlanRequest(BaseModel):
    include_observability: bool = True
    include_tests: bool = True
    include_runtime_apps: bool = True
    tech_debt_items: list[str] = Field(default_factory=list)
