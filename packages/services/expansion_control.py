from pydantic import BaseModel, Field


class ExpansionArmSummary(BaseModel):
    arm_name: str
    workspace_count: int = 0
    active_count: int = 0
    average_score: float = 0.0
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


class ExpansionControlSummary(BaseModel):
    total_workspace_count: int = 0
    total_active_count: int = 0
    arm_summaries: list[ExpansionArmSummary] = Field(default_factory=list)
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


def build_expansion_control_summary(arm_summaries: list[ExpansionArmSummary]) -> ExpansionControlSummary:
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    total_workspace_count = 0
    total_active_count = 0
    for arm in arm_summaries:
        total_workspace_count += arm.workspace_count
        total_active_count += arm.active_count
        for risk in arm.top_risks:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        for opportunity in arm.top_opportunities:
            opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    return ExpansionControlSummary(
        total_workspace_count=total_workspace_count,
        total_active_count=total_active_count,
        arm_summaries=arm_summaries,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
