from packages.domain.apps import AppRecord
from packages.domain.marketing import MarketingProject
from packages.domain.opportunity_hunter import OpportunityCandidate, OpportunityScan, OpportunityType


def build_active_app_opportunities(scan: OpportunityScan, apps: list[AppRecord]) -> list[OpportunityCandidate]:
    candidates: list[OpportunityCandidate] = []
    for app in apps:
        title = f"Expand {app.name} into adjacent workflow"
        summary = f"Use {app.name} as a wedge into nearby workflow or adjacent buyer need."
        candidates.append(
            OpportunityCandidate(
                scan_id=scan.id,
                title=title,
                opportunity_type=OpportunityType.active_app_expansion,
                summary=summary,
                target_users=[app.owner],
                related_apps=[app.id],
                related_industries=app.tags,
                evidence_notes=[{"source": "app_registry", "note": app.description}],
                demand_score=62.0,
                competition_score=48.0,
                whitespace_score=58.0,
                priority_score=61.0,
            )
        )
    return candidates


def build_marketing_adjacency_opportunities(scan: OpportunityScan, projects: list[MarketingProject]) -> list[OpportunityCandidate]:
    candidates: list[OpportunityCandidate] = []
    for project in projects:
        title = f"Underserved campaign tooling for {project.name} audience"
        summary = f"Find content, research, or execution tooling gaps around {project.name}."
        candidates.append(
            OpportunityCandidate(
                scan_id=scan.id,
                title=title,
                opportunity_type=OpportunityType.underserved_industry,
                summary=summary,
                target_users=project.audience,
                related_apps=project.linked_apps,
                related_industries=project.channels,
                evidence_notes=[{"source": "marketing_project", "note": project.description}],
                demand_score=59.0,
                competition_score=40.0,
                whitespace_score=72.0,
                priority_score=68.0,
            )
        )
    return candidates


def build_niche_opportunities(scan: OpportunityScan, terms: list[str]) -> list[OpportunityCandidate]:
    candidates: list[OpportunityCandidate] = []
    for term in terms:
        title = f"Niche opportunity around {term}"
        summary = f"Investigate whether {term} has concentrated need with weak software support."
        candidates.append(
            OpportunityCandidate(
                scan_id=scan.id,
                title=title,
                opportunity_type=OpportunityType.niche,
                summary=summary,
                target_users=[term],
                related_apps=[],
                related_industries=[term],
                evidence_notes=[{"source": "scan_query", "note": term}],
                demand_score=55.0,
                competition_score=35.0,
                whitespace_score=75.0,
                priority_score=67.0,
            )
        )
    return candidates
