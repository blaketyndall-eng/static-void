from pydantic import BaseModel, Field

from packages.domain.agent_studio import AgentStudioReview, AgentStudioSnapshot, AgentStudioWorkspace


class StudioOpsPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_routing_quality_score: float
    average_operator_confidence_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_STUDIO_OPS_ACTIONS = [
    'Define routing policies and approval checkpoints.',
    'Create replay tracks and operator review loops.',
    'Track budget controls and routing quality baselines.',
]


def review_studio_workspace(workspace: AgentStudioWorkspace, snapshot: AgentStudioSnapshot | None) -> AgentStudioReview:
    routing_quality = snapshot.routing_quality_score if snapshot is not None else 25.0
    operator_confidence = snapshot.operator_confidence_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.agent_roles) * 6 + len(workspace.routing_goals) * 6 + (0 if snapshot is None else len(snapshot.routing_policies) * 4),
            100,
        ),
        2,
    )
    review_score = round((routing_quality * 0.35) + (operator_confidence * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial orchestration snapshot.')
    if not workspace.agent_roles:
        actions.append('Define core roles and responsibilities.')
    if not workspace.routing_goals:
        actions.append('Define explicit routing goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk orchestration issue first.')
    actions.extend(DEFAULT_STUDIO_OPS_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return AgentStudioReview(
        workspace_id=workspace.id,
        review_score=review_score,
        orchestration_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on studio readiness.',
    )


def build_studio_summary(workspaces: list[AgentStudioWorkspace], snapshots: dict[str, AgentStudioSnapshot]) -> StudioOpsPortfolioSummary:
    if not workspaces:
        return StudioOpsPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_routing_quality_score=0.0,
            average_operator_confidence_score=0.0,
        )

    active_count = 0
    routing_scores = []
    confidence_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            routing_scores.append(snapshot.routing_quality_score)
            confidence_scores.append(snapshot.operator_confidence_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_routing = round(sum(routing_scores) / len(routing_scores), 2) if routing_scores else 0.0
    avg_confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return StudioOpsPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_routing_quality_score=avg_routing,
        average_operator_confidence_score=avg_confidence,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
