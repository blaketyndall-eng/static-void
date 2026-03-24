from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_blueprint_id(prefix: str = "blueprint") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AppTemplateType(str, Enum):
    operator_console = "operator_console"
    analyst_tool = "analyst_tool"
    decision_workflow = "decision_workflow"
    monitoring_dashboard = "monitoring_dashboard"
    reporting_app = "reporting_app"
    consumer_decision_app = "consumer_decision_app"


class BuildPacket(BaseModel):
    domain_modules: list[str] = Field(default_factory=list)
    contract_modules: list[str] = Field(default_factory=list)
    storage_modules: list[str] = Field(default_factory=list)
    repository_modules: list[str] = Field(default_factory=list)
    service_modules: list[str] = Field(default_factory=list)
    router_modules: list[str] = Field(default_factory=list)
    runtime_apps: list[str] = Field(default_factory=list)
    test_modules: list[str] = Field(default_factory=list)
    observability_modules: list[str] = Field(default_factory=list)


class AppBlueprint(BaseModel):
    id: str = Field(default_factory=new_blueprint_id)
    created_at: datetime = Field(default_factory=utc_now)
    name: str
    app_type: AppTemplateType
    description: str = ""
    target_users: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)
    required_engines: list[str] = Field(default_factory=list)
    primary_views: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    build_packet: BuildPacket = Field(default_factory=BuildPacket)
    notes: str = ""


class ScaffoldPlan(BaseModel):
    blueprint_id: str
    summary: str
    steps: list[str] = Field(default_factory=list)
    recommended_frameworks: list[str] = Field(default_factory=list)
    generated_files: list[str] = Field(default_factory=list)
    tech_debt_items: list[str] = Field(default_factory=list)
