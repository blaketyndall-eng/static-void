from pydantic import BaseModel, Field

from packages.domain.marketing import ContentAsset, MarketingAnalyticsSnapshot, MarketingProject, MarketingResearchRecord


class MarketingProjectReview(BaseModel):
    project_id: str
    project_name: str
    status: str
    research_score: float = Field(ge=0, le=100)
    content_score: float = Field(ge=0, le=100)
    analytics_score: float = Field(ge=0, le=100)
    review_score: float = Field(ge=0, le=100)
    lessons: list[str] = Field(default_factory=list)


class MarketingLearningSummary(BaseModel):
    total_projects: int
    active_projects: int
    average_review_score: float
    recurring_lessons: list[str] = Field(default_factory=list)
    by_status: dict[str, int] = Field(default_factory=dict)


def review_marketing_project(
    project: MarketingProject,
    research: MarketingResearchRecord | None,
    assets: list[ContentAsset],
    analytics: MarketingAnalyticsSnapshot | None,
) -> MarketingProjectReview:
    research_score = research.opportunity_score if research is not None else 35.0
    content_score = min(35 + len(assets) * 12, 100)
    if assets and any(asset.call_to_action for asset in assets):
        content_score += 10
    content_score = min(content_score, 100)
    analytics_score = analytics.quality_score if analytics is not None else 30.0
    review_score = round((research_score * 0.35) + (content_score * 0.3) + (analytics_score * 0.35), 2)

    lessons: list[str] = []
    if research is None:
        lessons.append("Add stronger market and competitor research before scaling execution.")
    if len(assets) == 0:
        lessons.append("Create at least one channel-ready content asset.")
    if analytics is None:
        lessons.append("Add analytics tracking before judging execution quality.")
    if analytics is not None and analytics.conversions == 0:
        lessons.append("Conversion path is weak; revisit CTA and channel-message fit.")
    if not lessons:
        lessons.append("Project foundation is solid. Improve iteration speed and channel-specific testing next.")

    return MarketingProjectReview(
        project_id=project.id,
        project_name=project.name,
        status=project.status.value,
        research_score=round(research_score, 2),
        content_score=round(content_score, 2),
        analytics_score=round(analytics_score, 2),
        review_score=review_score,
        lessons=lessons,
    )


def build_marketing_learning_summary(reviews: list[MarketingProjectReview]) -> MarketingLearningSummary:
    if not reviews:
        return MarketingLearningSummary(total_projects=0, active_projects=0, average_review_score=0.0, recurring_lessons=[], by_status={})

    lesson_counts: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for review in reviews:
        by_status[review.status] = by_status.get(review.status, 0) + 1
        for lesson in review.lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1

    recurring_lessons = [lesson for lesson, _count in sorted(lesson_counts.items(), key=lambda item: item[1], reverse=True)[:5]]
    active_projects = sum(1 for review in reviews if review.status == "active")
    average_review_score = round(sum(review.review_score for review in reviews) / len(reviews), 2)

    return MarketingLearningSummary(
        total_projects=len(reviews),
        active_projects=active_projects,
        average_review_score=average_review_score,
        recurring_lessons=recurring_lessons,
        by_status=by_status,
    )
