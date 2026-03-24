from pydantic import BaseModel, Field

from packages.domain.research_lab import ResearchLabReview, ResearchLabSnapshot, ResearchLabWorkspace


class ResearchLabPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_experiment_quality_score: float
    average_benchmark_confidence_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_RESEARCH_LAB_ACTIONS = [
    'Define champion-challenger experiment tracks.',
    'Create benchmark targets with review cadence.',
    'Promote winning variants into operational adoption.',
]


def review_research_lab_workspace(
    workspace: ResearchLabWorkspace,
    snapshot: ResearchLabSnapshot | None,
) -> ResearchLabReview:
    experiment_quality = snapshot.experiment_quality_score if snapshot is not None else 25.0
    benchmark_confidence = snapshot.benchmark_confidence_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.experiment_domains) * 6 + len(workspace.benchmark_targets) * 6 + (0 if snapshot is None else len(snapshot.active_experiments) * 4),
            100,
        ),
        2,
    )
    review_score = round((experiment_quality * 0.35) + (benchmark_confidence * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial research lab snapshot.')
    if not workspace.experiment_domains:
        actions.append('Define core experiment domains.')
    if not workspace.benchmark_targets:
        actions.append('Define benchmark targets and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk experiment or benchmark issue first.')
    actions.extend(DEFAULT_RESEARCH_LAB_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return ResearchLabReview(
        workspace_id=workspace.id,
        review_score=review_score,
        experiment_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on research lab readiness.',
    )


def build_research_lab_summary(
    workspaces: list[ResearchLabWorkspace],
    snapshots: dict[str, ResearchLabSnapshot],
) -> ResearchLabPortfolioSummary:
    if not workspaces:
        return ResearchLabPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_experiment_quality_score=0.0,
            average_benchmark_confidence_score=0.0,
        )

    active_count = 0
    experiment_scores = []
    benchmark_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'experimenting'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            experiment_scores.append(snapshot.experiment_quality_score)
            benchmark_scores.append(snapshot.benchmark_confidence_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_experiment = round(sum(experiment_scores) / len(experiment_scores), 2) if experiment_scores else 0.0
    avg_benchmark = round(sum(benchmark_scores) / len(benchmark_scores), 2) if benchmark_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return ResearchLabPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_experiment_quality_score=avg_experiment,
        average_benchmark_confidence_score=avg_benchmark,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
