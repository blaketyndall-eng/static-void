from pydantic import BaseModel, Field

from packages.domain.feedback_outcome_scoring import (
    FeedbackOutcomeScoringReview,
    FeedbackOutcomeScoringSnapshot,
    FeedbackOutcomeScoringWorkspace,
)


class FeedbackOutcomeScoringPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_outcome_quality_score: float
    average_feedback_readiness_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_FEEDBACK_ACTIONS = [
    'Define outcome review and prediction check ownership.',
    'Create usefulness scoring and regret signal workflows.',
    'Track feedback quality and outcome drift over time.',
]


def review_feedback_outcome_scoring_workspace(
    workspace: FeedbackOutcomeScoringWorkspace,
    snapshot: FeedbackOutcomeScoringSnapshot | None,
) -> FeedbackOutcomeScoringReview:
    outcome_quality = snapshot.outcome_quality_score if snapshot is not None else 25.0
    feedback_readiness = snapshot.feedback_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.outcome_domains) * 6 + len(workspace.scoring_goals) * 6 + (0 if snapshot is None else len(snapshot.outcome_reviews) * 4),
            100,
        ),
        2,
    )
    review_score = round((outcome_quality * 0.35) + (feedback_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial feedback and outcome scoring snapshot.')
    if not workspace.outcome_domains:
        actions.append('Define outcome domains and ownership.')
    if not workspace.scoring_goals:
        actions.append('Define explicit scoring goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-impact feedback risk first.')
    actions.extend(DEFAULT_FEEDBACK_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return FeedbackOutcomeScoringReview(
        workspace_id=workspace.id,
        review_score=review_score,
        feedback_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on feedback readiness.',
    )


def build_feedback_outcome_scoring_summary(
    workspaces: list[FeedbackOutcomeScoringWorkspace],
    snapshots: dict[str, FeedbackOutcomeScoringSnapshot],
) -> FeedbackOutcomeScoringPortfolioSummary:
    if not workspaces:
        return FeedbackOutcomeScoringPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_outcome_quality_score=0.0,
            average_feedback_readiness_score=0.0,
        )

    active_count = 0
    quality_scores = []
    readiness_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            quality_scores.append(snapshot.outcome_quality_score)
            readiness_scores.append(snapshot.feedback_readiness_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return FeedbackOutcomeScoringPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_outcome_quality_score=avg_quality,
        average_feedback_readiness_score=avg_readiness,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
