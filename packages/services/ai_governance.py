from pydantic import BaseModel, Field

from packages.domain.ai_governance import AIGovernanceReview, AIGovernanceSnapshot, AIGovernanceWorkspace


class AIGovernancePortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_governance_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_mitigations: list[str] = Field(default_factory=list)


DEFAULT_AI_GOV_ACTIONS = [
    'Define benchmark registry and evaluation cadence.',
    'Create policy checks for deployment approval.',
    'Add monitoring and post-deployment review checkpoints.',
]


def review_ai_governance_workspace(workspace: AIGovernanceWorkspace, snapshot: AIGovernanceSnapshot | None) -> AIGovernanceReview:
    governance_score = snapshot.governance_score if snapshot is not None else 25.0
    readiness = round(min(30 + len(workspace.evaluation_goals) * 8 + (0 if snapshot is None else len(snapshot.policy_checks) * 6), 100), 2)
    review_score = round((governance_score * 0.55) + (readiness * 0.45), 2)

    actions = []
    if snapshot is None:
        actions.append('Create initial governance snapshot and policy tracks.')
    if not workspace.evaluation_goals:
        actions.append('Define concrete evaluation goals and review criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Mitigate the highest-risk governance gap first.')
    actions.extend(DEFAULT_AI_GOV_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return AIGovernanceReview(
        workspace_id=workspace.id,
        review_score=review_score,
        approval_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on AI governance readiness.',
    )


def build_ai_governance_summary(workspaces: list[AIGovernanceWorkspace], snapshots: dict[str, AIGovernanceSnapshot]) -> AIGovernancePortfolioSummary:
    if not workspaces:
        return AIGovernancePortfolioSummary(workspace_count=0, active_count=0, average_governance_score=0.0)

    active_count = 0
    scores = []
    risk_counts: dict[str, int] = {}
    mitigation_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value == 'active':
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            scores.append(snapshot.governance_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for mitigation in snapshot.mitigations:
                mitigation_counts[mitigation] = mitigation_counts.get(mitigation, 0) + 1

    avg = round(sum(scores) / len(scores), 2) if scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_mitigations = [item for item, _count in sorted(mitigation_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return AIGovernancePortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_governance_score=avg,
        top_risks=top_risks,
        top_mitigations=top_mitigations,
    )
