from packages.domain.apps import AppRecord
from packages.domain.marketing import MarketingProject
from packages.domain.opportunity_hunter import OpportunityCandidate, OpportunityScan, OpportunityType


UNDERSERVED_INDUSTRY_SEEDS = [
    "industrial procurement",
    "specialty construction back office",
    "regional field services",
    "mid-market proposal operations",
    "compliance-heavy services firms",
]


WORKFLOW_GAP_SEEDS = [
    "handoff between research and execution",
    "content approval bottlenecks",
    "manual reporting and recap creation",
    "cross-system signal aggregation",
    "operator review queue prioritization",
]


def build_underserved_industry_opportunities(scan: OpportunityScan, industries: list[str] | None = None) -> list[OpportunityCandidate]:
    candidates: list[OpportunityCandidate] = []
    source_industries = industries or scan.source_queries or UNDERSERVED_INDUSTRY_SEEDS
    for industry in source_industries:
        title = f"Underserved software wedge for {industry}"
        summary = f"Investigate whether {industry} has fragmented demand, weak incumbents, and high workflow pain."
        candidates.append(
            OpportunityCandidate(
                scan_id=scan.id,
                title=title,
                opportunity_type=OpportunityType.underserved_industry,
                summary=summary,
                target_users=[industry],
                related_apps=[],
                related_industries=[industry],
                evidence_notes=[{"source": "underserved_seed", "note": industry}],
                demand_score=57.0,
                competition_score=34.0,
                whitespace_score=79.0,
                priority_score=71.0,
            )
        )
    return candidates


def build_workflow_gap_opportunities(scan: OpportunityScan, apps: list[AppRecord], projects: list[MarketingProject]) -> list[OpportunityCandidate]:
    candidates: list[OpportunityCandidate] = []

    for gap in WORKFLOW_GAP_SEEDS:
        title = f"Workflow gap opportunity: {gap}"
        related_apps = [app.id for app in apps[:3]]
        related_industries = []
        for project in projects[:3]:
            related_industries.extend(project.channels)
        candidates.append(
            OpportunityCandidate(
                scan_id=scan.id,
                title=title,
                opportunity_type=OpportunityType.workflow_gap,
                summary=f"Build a solution for the recurring workflow gap around {gap}.",
                target_users=["operators", "builders", "analysts"],
                related_apps=related_apps,
                related_industries=sorted(set(related_industries))[:5],
                evidence_notes=[{"source": "workflow_gap_seed", "note": gap}],
                demand_score=64.0,
                competition_score=42.0,
                whitespace_score=68.0,
                priority_score=69.0,
            )
        )
    return candidates
