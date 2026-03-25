from pydantic import BaseModel, Field

from packages.domain.bias_judgment_quality import (
    BiasJudgmentQualityReview,
    BiasJudgmentQualitySnapshot,
    BiasJudgmentQualityWorkspace,
)


class BiasJudgmentQualityPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_judgment_quality_score: float
    average_calibration_readiness_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_BIAS_ACTIONS = [
    'Define bias checks and calibration rule ownership.',
    'Create dissent prompts and assumption audit workflows.',
    'Track judgment quality and calibration readiness over time.',
]


def review_bias_judgment_quality_workspace(
    workspace: BiasJudgmentQualityWorkspace,
    snapshot: BiasJudgmentQualitySnapshot | None,
) -> BiasJudgmentQualityReview:
    judgment_quality = snapshot.judgment_quality_score if snapshot is not None else 25.0
    calibration_readiness = snapshot.calibration_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.judgment_domains) * 6 + len(workspace.quality_goals) * 6 + (0 if snapshot is None else len(snapshot.bias_checks) * 4),
            100,
        ),
        2,
    )
    review_score = round((judgment_quality * 0.35) + (calibration_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial bias and judgment quality snapshot.')
    if not workspace.judgment_domains:
        actions.append('Define judgment domains and ownership.')
    if not workspace.quality_goals:
        actions.append('Define explicit judgment quality goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-impact judgment risk first.')
    actions.extend(DEFAULT_BIAS_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return BiasJudgmentQualityReview(
        workspace_id=workspace.id,
        review_score=review_score,
        judgment_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on judgment readiness.',
    )


def build_bias_judgment_quality_summary(
    workspaces: list[BiasJudgmentQualityWorkspace],
    snapshots: dict[str, BiasJudgmentQualitySnapshot],
) -> BiasJudgmentQualityPortfolioSummary:
    if not workspaces:
        return BiasJudgmentQualityPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_judgment_quality_score=0.0,
            average_calibration_readiness_score=0.0,
        )

    active_count = 0
    quality_scores = []
    calibration_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            quality_scores.append(snapshot.judgment_quality_score)
            calibration_scores.append(snapshot.calibration_readiness_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0
    avg_calibration = round(sum(calibration_scores) / len(calibration_scores), 2) if calibration_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return BiasJudgmentQualityPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_judgment_quality_score=avg_quality,
        average_calibration_readiness_score=avg_calibration,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
