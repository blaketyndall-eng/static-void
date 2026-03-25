from pydantic import BaseModel, Field

from packages.domain.vertical_packs import VerticalPacksReview, VerticalPacksSnapshot, VerticalPacksWorkspace


class VerticalPacksPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_pack_quality_score: float
    average_adaptation_readiness_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_VERTICAL_PACK_ACTIONS = [
    'Define pack templates and domain playbooks.',
    'Create scoring models for target industries.',
    'Add reusable knowledge assets for adaptation.',
]


def review_vertical_pack_workspace(workspace: VerticalPacksWorkspace, snapshot: VerticalPacksSnapshot | None) -> VerticalPacksReview:
    pack_quality = snapshot.pack_quality_score if snapshot is not None else 25.0
    adaptation_readiness = snapshot.adaptation_readiness_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.industries) * 6 + len(workspace.pack_goals) * 6 + (0 if snapshot is None else len(snapshot.pack_templates) * 4),
            100,
        ),
        2,
    )
    review_score = round((pack_quality * 0.35) + (adaptation_readiness * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial vertical pack snapshot.')
    if not workspace.industries:
        actions.append('Define target industries for this pack.')
    if not workspace.pack_goals:
        actions.append('Define explicit pack goals and success criteria.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk pack adaptation issue first.')
    actions.extend(DEFAULT_VERTICAL_PACK_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return VerticalPacksReview(
        workspace_id=workspace.id,
        review_score=review_score,
        pack_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on vertical pack readiness.',
    )


def build_vertical_pack_summary(workspaces: list[VerticalPacksWorkspace], snapshots: dict[str, VerticalPacksSnapshot]) -> VerticalPacksPortfolioSummary:
    if not workspaces:
        return VerticalPacksPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_pack_quality_score=0.0,
            average_adaptation_readiness_score=0.0,
        )

    active_count = 0
    pack_scores = []
    readiness_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'designing'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            pack_scores.append(snapshot.pack_quality_score)
            readiness_scores.append(snapshot.adaptation_readiness_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_pack = round(sum(pack_scores) / len(pack_scores), 2) if pack_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return VerticalPacksPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_pack_quality_score=avg_pack,
        average_adaptation_readiness_score=avg_readiness,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
