from pydantic import BaseModel, Field

from packages.domain.company_operator import CompanyOperatorReview, CompanyOperatorSnapshot, CompanyOperatorWorkspace


class CompanyOperatorPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_operating_health_score: float
    average_execution_alignment_score: float
    top_blockers: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_COMPANY_OPERATOR_ACTIONS = [
    'Define company goals and operating cadence ownership.',
    'Track KPIs, initiatives, and blockers in one operating loop.',
    'Link major decisions directly to execution plans and owners.',
]


def review_company_operator_workspace(
    workspace: CompanyOperatorWorkspace,
    snapshot: CompanyOperatorSnapshot | None,
) -> CompanyOperatorReview:
    operating_health = snapshot.operating_health_score if snapshot is not None else 25.0
    execution_alignment = snapshot.execution_alignment_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.company_names) * 6 + len(workspace.operating_goals) * 6 + (0 if snapshot is None else len(snapshot.kpis) * 4),
            100,
        ),
        2,
    )
    review_score = round((operating_health * 0.35) + (execution_alignment * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial company operator snapshot.')
    if not workspace.company_names:
        actions.append('Define the companies this operator workspace manages.')
    if not workspace.operating_goals:
        actions.append('Define explicit operating goals and success criteria.')
    if snapshot is not None and snapshot.blockers:
        actions.append('Resolve the highest-impact operating blocker first.')
    actions.extend(DEFAULT_COMPANY_OPERATOR_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return CompanyOperatorReview(
        workspace_id=workspace.id,
        review_score=review_score,
        operator_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on operator readiness.',
    )


def build_company_operator_summary(
    workspaces: list[CompanyOperatorWorkspace],
    snapshots: dict[str, CompanyOperatorSnapshot],
) -> CompanyOperatorPortfolioSummary:
    if not workspaces:
        return CompanyOperatorPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_operating_health_score=0.0,
            average_execution_alignment_score=0.0,
        )

    active_count = 0
    health_scores = []
    alignment_scores = []
    blocker_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            health_scores.append(snapshot.operating_health_score)
            alignment_scores.append(snapshot.execution_alignment_score)
            for blocker in snapshot.blockers:
                blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_health = round(sum(health_scores) / len(health_scores), 2) if health_scores else 0.0
    avg_alignment = round(sum(alignment_scores) / len(alignment_scores), 2) if alignment_scores else 0.0
    top_blockers = [item for item, _count in sorted(blocker_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return CompanyOperatorPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_operating_health_score=avg_health,
        average_execution_alignment_score=avg_alignment,
        top_blockers=top_blockers,
        top_opportunities=top_opportunities,
    )
