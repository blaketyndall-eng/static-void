from pydantic import BaseModel, Field

from packages.domain.console_expansion import ConsoleArmReview, ConsoleArmSnapshot, ConsoleArmWorkspace


class ConsoleExpansionPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_maturity_score: float
    by_arm_type: dict[str, int] = Field(default_factory=dict)
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


ARM_DEFAULT_ACTIONS = {
    'ai_governance': ['Define evaluation and governance workflow.', 'Create benchmark registry.', 'Set policy and monitoring checkpoints.'],
    'signals_forecasting': ['Stand up signal scoring.', 'Define forecast confidence bands.', 'Create regime shift alerts.'],
    'research_lab': ['Create champion-challenger experiments.', 'Track experiment outcomes.', 'Promote winning variants.'],
    'agent_studio': ['Define routing policies.', 'Add HITL checkpoints.', 'Track tool budgets and replay.'],
    'vertical_packs': ['Define pack registry.', 'Create domain templates.', 'Add default scoring models.'],
    'decision_memory': ['Capture prior decisions.', 'Add outcome reviews.', 'Track regret and calibration.'],
    'integrations_automation': ['Map integration health.', 'Track automation workflows.', 'Add source freshness alerts.'],
    'data_source_intelligence': ['Track source quality.', 'Compare freshness.', 'Flag conflicts and gaps.'],
}


def review_console_arm(workspace: ConsoleArmWorkspace, snapshot: ConsoleArmSnapshot | None) -> ConsoleArmReview:
    maturity_score = snapshot.maturity_score if snapshot is not None else 25.0
    readiness_score = round(min(30 + len(workspace.goals) * 8 + (0 if snapshot is None else len(snapshot.active_tracks) * 6), 100), 2)
    review_score = round((maturity_score * 0.55) + (readiness_score * 0.45), 2)

    top_actions = []
    if snapshot is None:
        top_actions.append('Create an initial arm snapshot and operating focus.')
    if not workspace.goals:
        top_actions.append('Define concrete goals for this arm.')
    if snapshot is not None and snapshot.risks:
        top_actions.append('Reduce the highest-risk blocker first.')
    top_actions.extend(ARM_DEFAULT_ACTIONS.get(workspace.arm_type.value, [])[:2])
    top_actions = list(dict.fromkeys(top_actions))[:5]

    return ConsoleArmReview(
        workspace_id=workspace.id,
        review_score=review_score,
        readiness_score=readiness_score,
        top_actions=top_actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on console arm readiness.',
    )


def build_console_expansion_summary(workspaces: list[ConsoleArmWorkspace], snapshots: dict[str, ConsoleArmSnapshot]) -> ConsoleExpansionPortfolioSummary:
    if not workspaces:
        return ConsoleExpansionPortfolioSummary(workspace_count=0, active_count=0, average_maturity_score=0.0)

    by_arm_type: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    maturity_scores = []
    active_count = 0

    for workspace in workspaces:
        by_arm_type[workspace.arm_type.value] = by_arm_type.get(workspace.arm_type.value, 0) + 1
        if workspace.status.value == 'active':
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            maturity_scores.append(snapshot.maturity_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    average_maturity_score = round(sum(maturity_scores) / len(maturity_scores), 2) if maturity_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

    return ConsoleExpansionPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_maturity_score=average_maturity_score,
        by_arm_type=by_arm_type,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
