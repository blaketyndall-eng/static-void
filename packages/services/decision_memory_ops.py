from pydantic import BaseModel, Field

from packages.domain.decision_memory import DecisionMemoryReview, DecisionMemorySnapshot, DecisionMemoryWorkspace


class DecisionMemoryPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_memory_quality_score: float
    average_calibration_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_DECISION_MEMORY_ACTIONS = [
    'Capture decisions and their original rationale consistently.',
    'Add post-outcome reviews with clear success criteria.',
    'Promote reusable decision patterns into memory suggestions.',
]


def review_decision_memory_workspace(workspace: DecisionMemoryWorkspace, snapshot: DecisionMemorySnapshot | None) -> DecisionMemoryReview:
    memory_quality = snapshot.memory_quality_score if snapshot is not None else 25.0
    calibration = snapshot.calibration_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.memory_domains) * 6 + len(workspace.review_goals) * 6 + (0 if snapshot is None else len(snapshot.captured_decisions) * 3),
            100,
        ),
        2,
    )
    review_score = round((memory_quality * 0.35) + (calibration * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial decision memory snapshot.')
    if not workspace.memory_domains:
        actions.append('Define core decision memory domains.')
    if not workspace.review_goals:
        actions.append('Define explicit review and calibration goals.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk memory quality issue first.')
    actions.extend(DEFAULT_DECISION_MEMORY_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return DecisionMemoryReview(
        workspace_id=workspace.id,
        review_score=review_score,
        memory_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on decision memory readiness.',
    )


def build_decision_memory_summary(workspaces: list[DecisionMemoryWorkspace], snapshots: dict[str, DecisionMemorySnapshot]) -> DecisionMemoryPortfolioSummary:
    if not workspaces:
        return DecisionMemoryPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_memory_quality_score=0.0,
            average_calibration_score=0.0,
        )

    active_count = 0
    memory_scores = []
    calibration_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'reviewing'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            memory_scores.append(snapshot.memory_quality_score)
            calibration_scores.append(snapshot.calibration_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_memory = round(sum(memory_scores) / len(memory_scores), 2) if memory_scores else 0.0
    avg_calibration = round(sum(calibration_scores) / len(calibration_scores), 2) if calibration_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return DecisionMemoryPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_memory_quality_score=avg_memory,
        average_calibration_score=avg_calibration,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
