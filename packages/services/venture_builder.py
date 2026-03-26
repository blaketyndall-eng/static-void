from pydantic import BaseModel, Field

from packages.domain.venture_builder import (
    VentureBuilderReview,
    VentureBuilderSnapshot,
    VentureBuilderWorkspace,
)


class VentureBuilderPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_launch_readiness_score: float
    average_venture_confidence_score: float
    top_blockers: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_VENTURE_BUILDER_ACTIONS = [
    'Define the venture thesis and success criteria clearly.',
    'Map launch milestones, owners, and dependencies into one launch plan.',
    'Tie go/no-go evidence directly to decisions and launch execution.',
]


def review_venture_builder_workspace(
    workspace: VentureBuilderWorkspace,
    snapshot: VentureBuilderSnapshot | None,
) -> VentureBuilderReview:
    launch_readiness = snapshot.launch_readiness_score if snapshot is not None else 25.0
    venture_confidence = snapshot.venture_confidence_score if snapshot is not None else 25.0
    venture_readiness = round(
        min(
            30 + len(workspace.venture_ideas) * 6 + len(workspace.thesis_points) * 6 + (0 if snapshot is None else len(snapshot.launch_milestones) * 4),
            100,
        ),
        2,
    )
    review_score = round((launch_readiness * 0.35) + (venture_confidence * 0.35) + (venture_readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial venture builder snapshot.')
    if not workspace.venture_ideas:
        actions.append('Define the venture ideas this workspace is evaluating.')
    if not workspace.thesis_points:
        actions.append('Define explicit thesis points and validation criteria.')
    if snapshot is not None and snapshot.blockers:
        actions.append('Resolve the highest-impact launch blocker first.')
    actions.extend(DEFAULT_VENTURE_BUILDER_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return VentureBuilderReview(
        workspace_id=workspace.id,
        review_score=review_score,
        venture_readiness=venture_readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on venture readiness.',
    )


def build_venture_builder_summary(
    workspaces: list[VentureBuilderWorkspace],
    snapshots: dict[str, VentureBuilderSnapshot],
) -> VentureBuilderPortfolioSummary:
    if not workspaces:
        return VentureBuilderPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_launch_readiness_score=0.0,
            average_venture_confidence_score=0.0,
        )

    active_count = 0
    launch_scores = []
    confidence_scores = []
    blocker_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            launch_scores.append(snapshot.launch_readiness_score)
            confidence_scores.append(snapshot.venture_confidence_score)
            for blocker in snapshot.blockers:
                blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_launch = round(sum(launch_scores) / len(launch_scores), 2) if launch_scores else 0.0
    avg_confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0.0
    top_blockers = [item for item, _count in sorted(blocker_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return VentureBuilderPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_launch_readiness_score=avg_launch,
        average_venture_confidence_score=avg_confidence,
        top_blockers=top_blockers,
        top_opportunities=top_opportunities,
    )
