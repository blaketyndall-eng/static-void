from pydantic import BaseModel, Field

from packages.domain.workforce_coordination import (
    WorkforceCoordinationReview,
    WorkforceCoordinationSnapshot,
    WorkforceCoordinationWorkspace,
)


class WorkforceCoordinationPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_reliability_score: float
    average_readiness_score: float
    top_queue_pressures: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_WORKFORCE_ACTIONS = [
    'Define role groups and coordination ownership.',
    'Create routing rules, queue standards, and review points.',
    'Track escalation paths and tool access for every coordinated worker flow.',
]


def review_workforce_coordination_workspace(
    workspace: WorkforceCoordinationWorkspace,
    snapshot: WorkforceCoordinationSnapshot | None,
) -> WorkforceCoordinationReview:
    reliability = snapshot.reliability_score if snapshot is not None else 25.0
    readiness = snapshot.readiness_score if snapshot is not None else 25.0
    coordination_readiness = round(
        min(
            30 + len(workspace.role_groups) * 6 + len(workspace.coordination_goals) * 6 + (0 if snapshot is None else len(snapshot.work_queues) * 4),
            100,
        ),
        2,
    )
    review_score = round((reliability * 0.35) + (readiness * 0.35) + (coordination_readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial workforce coordination snapshot.')
    if not workspace.role_groups:
        actions.append('Define the worker role groups and ownership structure.')
    if not workspace.coordination_goals:
        actions.append('Define explicit coordination goals and success criteria.')
    if snapshot is not None and snapshot.work_queues:
        actions.append('Review the most critical queue and routing bottleneck first.')
    actions.extend(DEFAULT_WORKFORCE_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return WorkforceCoordinationReview(
        workspace_id=workspace.id,
        review_score=review_score,
        coordination_readiness=coordination_readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on workforce coordination readiness.',
    )


def build_workforce_coordination_summary(
    workspaces: list[WorkforceCoordinationWorkspace],
    snapshots: dict[str, WorkforceCoordinationSnapshot],
) -> WorkforceCoordinationPortfolioSummary:
    if not workspaces:
        return WorkforceCoordinationPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_reliability_score=0.0,
            average_readiness_score=0.0,
        )

    active_count = 0
    reliability_scores = []
    readiness_scores = []
    queue_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            reliability_scores.append(snapshot.reliability_score)
            readiness_scores.append(snapshot.readiness_score)
            for queue in snapshot.work_queues:
                queue_counts[queue] = queue_counts.get(queue, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_reliability = round(sum(reliability_scores) / len(reliability_scores), 2) if reliability_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_queue_pressures = [item for item, _count in sorted(queue_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return WorkforceCoordinationPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_reliability_score=avg_reliability,
        average_readiness_score=avg_readiness,
        top_queue_pressures=top_queue_pressures,
        top_opportunities=top_opportunities,
    )
