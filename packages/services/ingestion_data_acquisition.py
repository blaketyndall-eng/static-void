from pydantic import BaseModel, Field

from packages.domain.ingestion_data_acquisition import (
    IngestionDataAcquisitionReview,
    IngestionDataAcquisitionSnapshot,
    IngestionDataAcquisitionWorkspace,
)


class IngestionDataAcquisitionPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_ingestion_health_score: float
    average_normalization_readiness_score: float
    top_failures: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_INGESTION_ACTIONS = [
    'Define source connectors and sync ownership.',
    'Create normalization pipelines and freshness windows.',
    'Track failures with recovery and retry workflows.',
]


def review_ingestion_data_acquisition_workspace(
    workspace: IngestionDataAcquisitionWorkspace,
    snapshot: IngestionDataAcquisitionSnapshot | None,
) -> IngestionDataAcquisitionReview:
    ingestion_health = snapshot.ingestion_health_score if snapshot is not None else 25.0
    normalization_readiness = snapshot.normalization_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.source_targets) * 6 + len(workspace.ingestion_goals) * 6 + (0 if snapshot is None else len(snapshot.connectors) * 4),
            100,
        ),
        2,
    )
    review_score = round((ingestion_health * 0.35) + (normalization_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial ingestion and data acquisition snapshot.')
    if not workspace.source_targets:
        actions.append('Define source targets and sync ownership.')
    if not workspace.ingestion_goals:
        actions.append('Define explicit ingestion goals and success criteria.')
    if snapshot is not None and snapshot.failures:
        actions.append('Resolve the highest-impact ingestion failure first.')
    actions.extend(DEFAULT_INGESTION_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return IngestionDataAcquisitionReview(
        workspace_id=workspace.id,
        review_score=review_score,
        ingestion_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on ingestion readiness.',
    )


def build_ingestion_data_acquisition_summary(
    workspaces: list[IngestionDataAcquisitionWorkspace],
    snapshots: dict[str, IngestionDataAcquisitionSnapshot],
) -> IngestionDataAcquisitionPortfolioSummary:
    if not workspaces:
        return IngestionDataAcquisitionPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_ingestion_health_score=0.0,
            average_normalization_readiness_score=0.0,
        )

    active_count = 0
    health_scores = []
    normalization_scores = []
    failure_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            health_scores.append(snapshot.ingestion_health_score)
            normalization_scores.append(snapshot.normalization_readiness_score)
            for failure in snapshot.failures:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_health = round(sum(health_scores) / len(health_scores), 2) if health_scores else 0.0
    avg_normalization = round(sum(normalization_scores) / len(normalization_scores), 2) if normalization_scores else 0.0
    top_failures = [item for item, _count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return IngestionDataAcquisitionPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_ingestion_health_score=avg_health,
        average_normalization_readiness_score=avg_normalization,
        top_failures=top_failures,
        top_opportunities=top_opportunities,
    )
