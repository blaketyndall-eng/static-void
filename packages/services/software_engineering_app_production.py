from pydantic import BaseModel, Field

from packages.domain.app_builder import AppBlueprint
from packages.domain.software_engineering import EngineeringExecutionRecord, EngineeringExperimentRecord, EngineeringProject, EngineeringResearchRecord
from packages.services.software_engineering_engines import CUTTING_EDGE_TOOL_STACK


class AppProductionAdvisory(BaseModel):
    blueprint_id: str
    blueprint_name: str
    readiness_score: float = Field(ge=0, le=100)
    modernization_score: float = Field(ge=0, le=100)
    delivery_score: float = Field(ge=0, le=100)
    experimentation_score: float = Field(ge=0, le=100)
    recommended_stack: list[str] = Field(default_factory=list)
    production_priorities: list[str] = Field(default_factory=list)
    summary: str


class AppProductionPortfolioSummary(BaseModel):
    blueprint_count: int
    advisory_count: int
    average_readiness_score: float
    top_priorities: list[str] = Field(default_factory=list)
    recommended_stack: list[str] = Field(default_factory=list)


def build_app_production_advisory(
    blueprint: AppBlueprint,
    project: EngineeringProject | None,
    research: EngineeringResearchRecord | None,
    execution: EngineeringExecutionRecord | None,
    experiments: EngineeringExperimentRecord | None,
) -> AppProductionAdvisory:
    modernization_score = research.modernization_score if research is not None else 35.0
    delivery_score = ((execution.reliability_score + execution.delivery_score) / 2) if execution is not None else 35.0
    experimentation_score = experiments.experimentation_score if experiments is not None else 30.0
    readiness_score = round((modernization_score * 0.35) + (delivery_score * 0.45) + (experimentation_score * 0.2), 2)

    recommended_stack = []
    if research is not None:
        recommended_stack.extend(research.tool_recommendations)
    for values in CUTTING_EDGE_TOOL_STACK.values():
        recommended_stack.extend(values)
    recommended_stack = list(dict.fromkeys(recommended_stack))[:10]

    priorities = []
    if modernization_score < 70:
        priorities.append("Modernize the production stack and reduce legacy build friction.")
    if delivery_score < 70:
        priorities.append("Improve CI reliability, task orchestration, and release confidence.")
    if experimentation_score < 60:
        priorities.append("Run targeted experiments on faster tooling and observability upgrades.")
    if not project:
        priorities.append("Link an engineering project directly to this app blueprint.")
    if not priorities:
        priorities.append("Advance this blueprint into a production-ready implementation plan.")

    return AppProductionAdvisory(
        blueprint_id=blueprint.id,
        blueprint_name=blueprint.name,
        readiness_score=readiness_score,
        modernization_score=round(modernization_score, 2),
        delivery_score=round(delivery_score, 2),
        experimentation_score=round(experimentation_score, 2),
        recommended_stack=recommended_stack,
        production_priorities=priorities,
        summary=f"App production readiness for {blueprint.name} scored {readiness_score:.1f}/100.",
    )


def build_app_production_portfolio_summary(advisories: list[AppProductionAdvisory]) -> AppProductionPortfolioSummary:
    if not advisories:
        return AppProductionPortfolioSummary(
            blueprint_count=0,
            advisory_count=0,
            average_readiness_score=0.0,
            top_priorities=[],
            recommended_stack=[],
        )

    priority_counts: dict[str, int] = {}
    stack_counts: dict[str, int] = {}
    for advisory in advisories:
        for priority in advisory.production_priorities:
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        for tool in advisory.recommended_stack:
            stack_counts[tool] = stack_counts.get(tool, 0) + 1

    top_priorities = [item for item, _count in sorted(priority_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    recommended_stack = [item for item, _count in sorted(stack_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    average_readiness_score = round(sum(item.readiness_score for item in advisories) / len(advisories), 2)

    return AppProductionPortfolioSummary(
        blueprint_count=len(advisories),
        advisory_count=len(advisories),
        average_readiness_score=average_readiness_score,
        top_priorities=top_priorities,
        recommended_stack=recommended_stack,
    )
