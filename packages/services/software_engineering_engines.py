from pydantic import BaseModel, Field

from packages.domain.software_engineering import (
    EngineeringExecutionRecord,
    EngineeringExperimentRecord,
    EngineeringProject,
    EngineeringResearchRecord,
)


class EngineeringResearchEvaluation(BaseModel):
    project_id: str
    modernization_score: float = Field(ge=0, le=100)
    architecture_score: float = Field(ge=0, le=100)
    performance_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    recommended_stack: list[str] = Field(default_factory=list)
    summary: str


class EngineeringExecutionEvaluation(BaseModel):
    project_id: str
    reliability_score: float = Field(ge=0, le=100)
    delivery_score: float = Field(ge=0, le=100)
    blocker_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    priorities: list[str] = Field(default_factory=list)
    summary: str


class EngineeringExperimentEvaluation(BaseModel):
    project_id: str
    experimentation_score: float = Field(ge=0, le=100)
    adoption_readiness_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    adoption_candidates: list[str] = Field(default_factory=list)
    summary: str


CUTTING_EDGE_TOOL_STACK = {
    "python_tooling": ["uv", "Ruff"],
    "javascript_tooling": ["Biome", "Bun"],
    "testing": ["Vitest", "Playwright"],
    "observability": ["OpenTelemetry"],
}


def evaluate_engineering_research(project: EngineeringProject, record: EngineeringResearchRecord) -> EngineeringResearchEvaluation:
    architecture_score = min(35 + len(record.architecture_notes) * 10, 100)
    performance_score = min(35 + len(record.performance_findings) * 10, 100)
    modernization_score = max(record.modernization_score, min(30 + len(record.tool_recommendations) * 12, 100))
    confidence_score = round((architecture_score * 0.35) + (performance_score * 0.25) + (modernization_score * 0.4), 2)
    recommended_stack = list(dict.fromkeys(record.tool_recommendations + CUTTING_EDGE_TOOL_STACK.get("python_tooling", []) + CUTTING_EDGE_TOOL_STACK.get("javascript_tooling", [])))[:8]
    return EngineeringResearchEvaluation(
        project_id=project.id,
        modernization_score=modernization_score,
        architecture_score=architecture_score,
        performance_score=performance_score,
        confidence_score=confidence_score,
        recommended_stack=recommended_stack,
        summary=f"Engineering research confidence scored {confidence_score:.1f}/100 for {project.name}.",
    )


def evaluate_engineering_execution(project: EngineeringProject, record: EngineeringExecutionRecord) -> EngineeringExecutionEvaluation:
    blocker_penalty = min(len(record.blockers) * 12, 60)
    blocker_score = max(100 - blocker_penalty, 0)
    confidence_score = round((record.reliability_score * 0.4) + (record.delivery_score * 0.4) + (blocker_score * 0.2), 2)
    priorities = []
    if record.reliability_score < 70:
        priorities.append("Improve reliability and observability baselines.")
    if record.delivery_score < 70:
        priorities.append("Tighten delivery workflows and reduce queue time.")
    if record.blockers:
        priorities.append("Resolve the highest-cost blockers first.")
    if not priorities:
        priorities.append("Move into performance and DX refinements.")
    return EngineeringExecutionEvaluation(
        project_id=project.id,
        reliability_score=record.reliability_score,
        delivery_score=record.delivery_score,
        blocker_score=blocker_score,
        confidence_score=confidence_score,
        priorities=priorities,
        summary=f"Execution confidence scored {confidence_score:.1f}/100 for {project.name}.",
    )


def evaluate_engineering_experiments(project: EngineeringProject, record: EngineeringExperimentRecord) -> EngineeringExperimentEvaluation:
    adoption_readiness_score = min(35 + len(record.adoption_candidates) * 12 + len(record.findings) * 6, 100)
    confidence_score = round((record.experimentation_score * 0.55) + (adoption_readiness_score * 0.45), 2)
    return EngineeringExperimentEvaluation(
        project_id=project.id,
        experimentation_score=record.experimentation_score,
        adoption_readiness_score=adoption_readiness_score,
        confidence_score=confidence_score,
        adoption_candidates=record.adoption_candidates[:10],
        summary=f"Experimentation confidence scored {confidence_score:.1f}/100 for {project.name}.",
    )
