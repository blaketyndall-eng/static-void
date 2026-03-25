from pydantic import BaseModel, Field

from packages.domain.output_briefing_engine import (
    OutputBriefingEngineReview,
    OutputBriefingEngineSnapshot,
    OutputBriefingEngineWorkspace,
)


class OutputBriefingEnginePortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_output_quality_score: float
    average_briefing_readiness_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_OUTPUT_ACTIONS = [
    'Define briefing templates and evidence pack standards.',
    'Create distribution rules and alert formats.',
    'Track output quality and audience readiness.',
]


def review_output_briefing_engine_workspace(
    workspace: OutputBriefingEngineWorkspace,
    snapshot: OutputBriefingEngineSnapshot | None,
) -> OutputBriefingEngineReview:
    output_quality = snapshot.output_quality_score if snapshot is not None else 25.0
    briefing_readiness = snapshot.briefing_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.briefing_domains) * 6 + len(workspace.output_goals) * 6 + (0 if snapshot is None else len(snapshot.briefing_templates) * 4),
            100,
        ),
        2,
    )
    review_score = round((output_quality * 0.35) + (briefing_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial output and briefing engine snapshot.')
    if not workspace.briefing_domains:
        actions.append('Define briefing domains and ownership.')
    if not workspace.output_goals:
        actions.append('Define explicit output goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-impact output risk first.')
    actions.extend(DEFAULT_OUTPUT_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return OutputBriefingEngineReview(
        workspace_id=workspace.id,
        review_score=review_score,
        output_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on output readiness.',
    )


def build_output_briefing_engine_summary(
    workspaces: list[OutputBriefingEngineWorkspace],
    snapshots: dict[str, OutputBriefingEngineSnapshot],
) -> OutputBriefingEnginePortfolioSummary:
    if not workspaces:
        return OutputBriefingEnginePortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_output_quality_score=0.0,
            average_briefing_readiness_score=0.0,
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
            quality_scores.append(snapshot.output_quality_score)
            readiness_scores.append(snapshot.briefing_readiness_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return OutputBriefingEnginePortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_output_quality_score=avg_quality,
        average_briefing_readiness_score=avg_readiness,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
