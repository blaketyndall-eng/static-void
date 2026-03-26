from pydantic import BaseModel, Field

from packages.domain.action_workflow_execution import (
    ActionWorkflowExecutionReview,
    ActionWorkflowExecutionSnapshot,
    ActionWorkflowExecutionWorkspace,
)


class ActionWorkflowExecutionPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_execution_reliability_score: float
    average_approval_readiness_score: float
    top_failures: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_ACTION_EXECUTION_ACTIONS = [
    'Define workflow templates and execution ownership.',
    'Create approval checkpoints and connector action policies.',
    'Track execution failures and recovery workflows.',
]


def review_action_workflow_execution_workspace(
    workspace: ActionWorkflowExecutionWorkspace,
    snapshot: ActionWorkflowExecutionSnapshot | None,
) -> ActionWorkflowExecutionReview:
    execution_reliability = snapshot.execution_reliability_score if snapshot is not None else 25.0
    approval_readiness = snapshot.approval_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.execution_domains) * 6 + len(workspace.workflow_goals) * 6 + (0 if snapshot is None else len(snapshot.workflow_templates) * 4),
            100,
        ),
        2,
    )
    review_score = round((execution_reliability * 0.35) + (approval_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial action and workflow execution snapshot.')
    if not workspace.execution_domains:
        actions.append('Define execution domains and ownership.')
    if not workspace.workflow_goals:
        actions.append('Define explicit workflow goals and success criteria.')
    if snapshot is not None and snapshot.failure_modes:
        actions.append('Reduce the highest-impact execution failure first.')
    actions.extend(DEFAULT_ACTION_EXECUTION_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return ActionWorkflowExecutionReview(
        workspace_id=workspace.id,
        review_score=review_score,
        execution_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on execution readiness.',
    )


def build_action_workflow_execution_summary(
    workspaces: list[ActionWorkflowExecutionWorkspace],
    snapshots: dict[str, ActionWorkflowExecutionSnapshot],
) -> ActionWorkflowExecutionPortfolioSummary:
    if not workspaces:
        return ActionWorkflowExecutionPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_execution_reliability_score=0.0,
            average_approval_readiness_score=0.0,
        )

    active_count = 0
    reliability_scores = []
    approval_scores = []
    failure_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            reliability_scores.append(snapshot.execution_reliability_score)
            approval_scores.append(snapshot.approval_readiness_score)
            for failure in snapshot.failure_modes:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_reliability = round(sum(reliability_scores) / len(reliability_scores), 2) if reliability_scores else 0.0
    avg_approval = round(sum(approval_scores) / len(approval_scores), 2) if approval_scores else 0.0
    top_failures = [item for item, _count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return ActionWorkflowExecutionPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_execution_reliability_score=avg_reliability,
        average_approval_readiness_score=avg_approval,
        top_failures=top_failures,
        top_opportunities=top_opportunities,
    )
