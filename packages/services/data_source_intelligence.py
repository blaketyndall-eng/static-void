from pydantic import BaseModel, Field

from packages.domain.data_source_intelligence import (
    DataSourceIntelligenceReview,
    DataSourceIntelligenceSnapshot,
    DataSourceIntelligenceWorkspace,
)


class DataSourceIntelligencePortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_source_quality_score: float
    average_freshness_confidence_score: float
    top_conflicts: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_SOURCE_INTELLIGENCE_ACTIONS = [
    'Define source health and freshness checks.',
    'Track reliability flags and conflicts consistently.',
    'Close the highest-impact coverage gaps first.',
]


def review_data_source_intelligence_workspace(
    workspace: DataSourceIntelligenceWorkspace,
    snapshot: DataSourceIntelligenceSnapshot | None,
) -> DataSourceIntelligenceReview:
    source_quality = snapshot.source_quality_score if snapshot is not None else 25.0
    freshness_confidence = snapshot.freshness_confidence_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.source_domains) * 6 + len(workspace.intelligence_goals) * 6 + (0 if snapshot is None else len(snapshot.source_health_checks) * 4),
            100,
        ),
        2,
    )
    review_score = round((source_quality * 0.35) + (freshness_confidence * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial data source intelligence snapshot.')
    if not workspace.source_domains:
        actions.append('Define source domains and ownership.')
    if not workspace.intelligence_goals:
        actions.append('Define explicit source intelligence goals.')
    if snapshot is not None and snapshot.conflict_detections:
        actions.append('Resolve the highest-impact source conflict first.')
    actions.extend(DEFAULT_SOURCE_INTELLIGENCE_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return DataSourceIntelligenceReview(
        workspace_id=workspace.id,
        review_score=review_score,
        source_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on data source intelligence readiness.',
    )


def build_data_source_intelligence_summary(
    workspaces: list[DataSourceIntelligenceWorkspace],
    snapshots: dict[str, DataSourceIntelligenceSnapshot],
) -> DataSourceIntelligencePortfolioSummary:
    if not workspaces:
        return DataSourceIntelligencePortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_source_quality_score=0.0,
            average_freshness_confidence_score=0.0,
        )

    active_count = 0
    quality_scores = []
    freshness_scores = []
    conflict_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            quality_scores.append(snapshot.source_quality_score)
            freshness_scores.append(snapshot.freshness_confidence_score)
            for conflict in snapshot.conflict_detections:
                conflict_counts[conflict] = conflict_counts.get(conflict, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_quality = round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0
    avg_freshness = round(sum(freshness_scores) / len(freshness_scores), 2) if freshness_scores else 0.0
    top_conflicts = [item for item, _count in sorted(conflict_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return DataSourceIntelligencePortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_source_quality_score=avg_quality,
        average_freshness_confidence_score=avg_freshness,
        top_conflicts=top_conflicts,
        top_opportunities=top_opportunities,
    )
