from packages.domain.apps import AppRecord
from packages.domain.marketing import MarketingProject
from packages.domain.opportunity_hunter import OpportunityScan
from packages.services.opportunity_hunter_scanners import (
    build_active_app_opportunities,
    build_marketing_adjacency_opportunities,
    build_niche_opportunities,
)
from packages.services.opportunity_hunter_scanners_v2 import (
    build_underserved_industry_opportunities,
    build_workflow_gap_opportunities,
)


def build_auto_scan(name: str = "Auto Opportunity Sweep") -> OpportunityScan:
    return OpportunityScan(
        name=name,
        focus="Automatically scan active system state for app-adjacent, niche, underserved, and workflow-gap opportunities.",
        source_arms=["apps", "marketing", "master_console"],
        source_queries=["workflow automation", "underserved industry", "adjacent software wedge"],
        notes="Generated from current state of active apps and projects.",
    )


def generate_auto_scan_candidates(scan: OpportunityScan, apps: list[AppRecord], projects: list[MarketingProject]) -> list:
    niche_terms = []
    for app in apps[:5]:
        niche_terms.extend(app.tags)
    for project in projects[:5]:
        niche_terms.extend(project.channels)
        niche_terms.extend(project.audience)
    niche_terms = [item for item in dict.fromkeys(niche_terms) if item]

    candidates = []
    candidates.extend(build_active_app_opportunities(scan, apps))
    candidates.extend(build_marketing_adjacency_opportunities(scan, projects))
    candidates.extend(build_niche_opportunities(scan, niche_terms[:8]))
    candidates.extend(build_underserved_industry_opportunities(scan, None))
    candidates.extend(build_workflow_gap_opportunities(scan, apps, projects))
    return candidates
