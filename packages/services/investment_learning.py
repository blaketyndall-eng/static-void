from pydantic import BaseModel, Field

from packages.domain.investment import InvestmentThesis


class ThesisReview(BaseModel):
    thesis_id: str
    ticker: str
    status: str
    recommendation_state: str
    conviction: float
    catalyst_count: int
    risk_flag_count: int
    review_score: float = Field(ge=0, le=100)
    outcome_label: str
    lessons: list[str] = Field(default_factory=list)


class LearningSummary(BaseModel):
    total_theses: int
    active_count: int
    reviewed_count: int
    invalidated_count: int
    average_conviction: float
    average_review_score: float
    by_outcome: dict[str, int] = Field(default_factory=dict)
    recurring_lessons: list[str] = Field(default_factory=list)


def review_thesis(thesis: InvestmentThesis) -> ThesisReview:
    review_score = 45.0
    review_score += thesis.conviction * 20
    review_score += min(len(thesis.catalysts) * 8, 16)
    review_score -= min(len(thesis.risk_flags) * 5, 15)
    if thesis.invalidation:
        review_score += 10
    if thesis.entry_zone and thesis.target_zone:
        review_score += 10
    review_score = max(0.0, min(review_score, 100.0))

    if thesis.status.value == "reviewed":
        outcome_label = "reviewed"
    elif thesis.status.value == "invalidated":
        outcome_label = "invalidated"
    elif thesis.status.value in {"active", "scaling"}:
        outcome_label = "live"
    else:
        outcome_label = "watch"

    lessons: list[str] = []
    if not thesis.invalidation:
        lessons.append("Add a clearer invalidation level.")
    if len(thesis.catalysts) == 0:
        lessons.append("Add at least one catalyst or timing reason.")
    if len(thesis.risk_flags) > 2:
        lessons.append("Risk stack may be too dense for current conviction.")
    if thesis.conviction < 0.5:
        lessons.append("Conviction is modest; consider watchlist instead of active sizing.")
    if not lessons:
        lessons.append("Thesis structure is reasonably complete. Review outcome and sizing discipline next.")

    return ThesisReview(
        thesis_id=thesis.id,
        ticker=thesis.ticker,
        status=thesis.status.value,
        recommendation_state=thesis.recommendation_state.value,
        conviction=thesis.conviction,
        catalyst_count=len(thesis.catalysts),
        risk_flag_count=len(thesis.risk_flags),
        review_score=round(review_score, 2),
        outcome_label=outcome_label,
        lessons=lessons,
    )


def build_learning_summary(theses: list[InvestmentThesis]) -> LearningSummary:
    if not theses:
        return LearningSummary(
            total_theses=0,
            active_count=0,
            reviewed_count=0,
            invalidated_count=0,
            average_conviction=0.0,
            average_review_score=0.0,
            by_outcome={},
            recurring_lessons=[],
        )

    reviews = [review_thesis(thesis) for thesis in theses]
    by_outcome: dict[str, int] = {}
    lesson_counts: dict[str, int] = {}
    for review in reviews:
        by_outcome[review.outcome_label] = by_outcome.get(review.outcome_label, 0) + 1
        for lesson in review.lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1

    recurring_lessons = [
        lesson for lesson, _count in sorted(lesson_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    ]

    return LearningSummary(
        total_theses=len(theses),
        active_count=sum(1 for thesis in theses if thesis.status.value in {"active", "scaling"}),
        reviewed_count=sum(1 for thesis in theses if thesis.status.value == "reviewed"),
        invalidated_count=sum(1 for thesis in theses if thesis.status.value == "invalidated"),
        average_conviction=round(sum(thesis.conviction for thesis in theses) / len(theses), 3),
        average_review_score=round(sum(review.review_score for review in reviews) / len(reviews), 2),
        by_outcome=by_outcome,
        recurring_lessons=recurring_lessons,
    )
