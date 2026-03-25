from pydantic import BaseModel, Field

from packages.domain.benchmark_harness import (
    BenchmarkHarnessReview,
    BenchmarkHarnessSnapshot,
    BenchmarkHarnessWorkspace,
)


class BenchmarkHarnessPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_benchmark_quality_score: float
    average_harness_readiness_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_BENCHMARK_ACTIONS = [
    'Define benchmark suites and replay dataset ownership.',
    'Create challenger model evaluation and rollback rules.',
    'Track harness quality and benchmark drift over time.',
]


def review_benchmark_harness_workspace(
    workspace: BenchmarkHarnessWorkspace,
    snapshot: BenchmarkHarnessSnapshot | None,
) -> BenchmarkHarnessReview:
    benchmark_quality = snapshot.benchmark_quality_score if snapshot is not None else 25.0
    harness_readiness = snapshot.harness_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.benchmark_domains) * 6 + len(workspace.benchmark_goals) * 6 + (0 if snapshot is None else len(snapshot.benchmark_suites) * 4),
            100,
        ),
        2,
    )
    review_score = round((benchmark_quality * 0.35) + (harness_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial benchmark harness snapshot.')
    if not workspace.benchmark_domains:
        actions.append('Define benchmark domains and ownership.')
    if not workspace.benchmark_goals:
        actions.append('Define explicit benchmark goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-impact benchmark risk first.')
    actions.extend(DEFAULT_BENCHMARK_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return BenchmarkHarnessReview(
        workspace_id=workspace.id,
        review_score=review_score,
        benchmark_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on benchmark readiness.',
    )


def build_benchmark_harness_summary(
    workspaces: list[BenchmarkHarnessWorkspace],
    snapshots: dict[str, BenchmarkHarnessSnapshot],
) -> BenchmarkHarnessPortfolioSummary:
    if not workspaces:
        return BenchmarkHarnessPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_benchmark_quality_score=0.0,
            average_harness_readiness_score=0.0,
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
            quality_scores.append(snapshot.benchmark_quality_score)
            readiness_scores.append(snapshot.harness_readiness_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return BenchmarkHarnessPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_benchmark_quality_score=avg_quality,
        average_harness_readiness_score=avg_readiness,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
