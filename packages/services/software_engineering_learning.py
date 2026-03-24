from pydantic import BaseModel, Field

from packages.domain.software_engineering import (
    EngineeringExecutionRecord,
    EngineeringExperimentRecord,
    EngineeringProject,
    EngineeringResearchRecord,
)


class EngineeringProjectReview(BaseModel):
    project_id: str
    project_name: str
    status: str
    research_score: float = Field(ge=0, le=100)
    execution_score: float = Field(ge=0, le=100)
    experimentation_score: float = Field(ge=0, le=100)
    review_score: float = Field(ge=0, le=100)
    lessons: list[str] = Field(default_factory=list)


class EngineeringLearningSummary(BaseModel):
    total_projects: int
    active_projects: int
    average_review_score: float
    recurring_lessons: list[str] = Field(default_factory=list)
    by_status: dict[str, int] = Field(default_factory=dict)


def review_engineering_project(
    project: EngineeringProject,
    research: EngineeringResearchRecord | None,
    execution: EngineeringExecutionRecord | None,
    experiments: EngineeringExperimentRecord | None,
) -> EngineeringProjectReview:
    research_score = research.modernization_score if research is not None else 35.0
    execution_score = round(((execution.reliability_score + execution.delivery_score) / 2), 2) if execution is not None else 35.0
    experimentation_score = experiments.experimentation_score if experiments is not None else 30.0
    review_score = round((research_score * 0.3) + (execution_score * 0.45) + (experimentation_score * 0.25), 2)

    lessons: list[str] = []
    if research is None:
        lessons.append("Add stronger architecture and modernization research.")
    if execution is None:
        lessons.append("Track active work, blockers, and reliability before scaling execution.")
    elif execution.blockers:
        lessons.append("Resolve the top execution blockers reducing delivery throughput.")
    if experiments is None:
        lessons.append("Create a lightweight experimentation backlog for future-stack validation.")
    elif not experiments.adoption_candidates:
        lessons.append("Translate experiments into concrete adoption candidates.")
    if not lessons:
        lessons.append("Project foundation is strong. Push on performance, DX, and selective adoption of new tooling.")

    return EngineeringProjectReview(
        project_id=project.id,
        project_name=project.name,
        status=project.status.value,
        research_score=round(research_score, 2),
        execution_score=round(execution_score, 2),
        experimentation_score=round(experimentation_score, 2),
        review_score=review_score,
        lessons=lessons,
    )


def build_engineering_learning_summary(reviews: list[EngineeringProjectReview]) -> EngineeringLearningSummary:
    if not reviews:
        return EngineeringLearningSummary(total_projects=0, active_projects=0, average_review_score=0.0, recurring_lessons=[], by_status={})

    lesson_counts: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for review in reviews:
        by_status[review.status] = by_status.get(review.status, 0) + 1
        for lesson in review.lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1

    recurring_lessons = [lesson for lesson, _count in sorted(lesson_counts.items(), key=lambda item: item[1], reverse=True)[:5]]
    active_projects = sum(1 for review in reviews if review.status == "active")
    average_review_score = round(sum(review.review_score for review in reviews) / len(reviews), 2)

    return EngineeringLearningSummary(
        total_projects=len(reviews),
        active_projects=active_projects,
        average_review_score=average_review_score,
        recurring_lessons=recurring_lessons,
        by_status=by_status,
    )
