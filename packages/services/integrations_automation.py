from pydantic import BaseModel, Field

from packages.domain.integrations_automation import (
    IntegrationsAutomationReview,
    IntegrationsAutomationSnapshot,
    IntegrationsAutomationWorkspace,
)


class IntegrationsAutomationPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_integration_health_score: float
    average_automation_reliability_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_INTEGRATION_ACTIONS = [
    'Define integration health checks and owners.',
    'Create automation workflows with reliability baselines.',
    'Add freshness and webhook alerting.',
]


def review_integrations_automation_workspace(
    workspace: IntegrationsAutomationWorkspace,
    snapshot: IntegrationsAutomationSnapshot | None,
) -> IntegrationsAutomationReview:
    integration_health = snapshot.integration_health_score if snapshot is not None else 25.0
    automation_reliability = snapshot.automation_reliability_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.integration_targets) * 6 + len(workspace.automation_goals) * 6 + (0 if snapshot is None else len(snapshot.automation_workflows) * 4),
            100,
        ),
        2,
    )
    review_score = round((integration_health * 0.35) + (automation_reliability * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial integrations and automation snapshot.')
    if not workspace.integration_targets:
        actions.append('Define integration targets and ownership.')
    if not workspace.automation_goals:
        actions.append('Define explicit automation goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk integration issue first.')
    actions.extend(DEFAULT_INTEGRATION_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return IntegrationsAutomationReview(
        workspace_id=workspace.id,
        review_score=review_score,
        automation_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on integrations and automation readiness.',
    )


def build_integrations_automation_summary(
    workspaces: list[IntegrationsAutomationWorkspace],
    snapshots: dict[str, IntegrationsAutomationSnapshot],
) -> IntegrationsAutomationPortfolioSummary:
    if not workspaces:
        return IntegrationsAutomationPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_integration_health_score=0.0,
            average_automation_reliability_score=0.0,
        )

    active_count = 0
    health_scores = []
    reliability_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            health_scores.append(snapshot.integration_health_score)
            reliability_scores.append(snapshot.automation_reliability_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_health = round(sum(health_scores) / len(health_scores), 2) if health_scores else 0.0
    avg_reliability = round(sum(reliability_scores) / len(reliability_scores), 2) if reliability_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return IntegrationsAutomationPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_integration_health_score=avg_health,
        average_automation_reliability_score=avg_reliability,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
