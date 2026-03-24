from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.apps import AppRepository
from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.brain_links import BrainLinkRepository
from packages.repositories.investment import InvestmentThesisRepository
from packages.repositories.marketing import MarketingProjectRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.repositories.software_engineering import (
    EngineeringExecutionRepository,
    EngineeringExperimentRepository,
    EngineeringProjectRepository,
    EngineeringResearchRepository,
)
from packages.repositories.system_events import SystemEventRepository
from packages.services.se_app_linking import find_best_linked_project, score_blueprint_project_match
from packages.services.software_engineering_app_production import (
    build_app_production_advisory,
    build_app_production_portfolio_summary,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/master-console', tags=['master_console_v4'])
telemetry = TelemetryLogger(filepath='var/master_console_telemetry.jsonl')


@router.get('/summary-v4')
def get_master_console_summary_v4(db: Session = Depends(get_db)) -> dict:
    apps = AppRepository(db).list()
    blueprints = AppBlueprintRepository(db).list()
    marketing_projects = MarketingProjectRepository(db).list()
    scans = OpportunityScanRepository(db).list()
    opp_repo = OpportunityCandidateRepository(db)
    opportunity_candidates = []
    for scan in scans:
        opportunity_candidates.extend(opp_repo.list_for_scan(scan.id))
    investments = InvestmentThesisRepository(db).list()
    brain_links = BrainLinkRepository(db).list()
    module_summary = [item.model_dump(mode='json') for item in BrainLinkRepository(db).summarize_modules()]
    system_events = [item.model_dump(mode='json') for item in SystemEventRepository(db).list()]

    engineering_projects = EngineeringProjectRepository(db).list()
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)
    advisories = []
    linkage_notes = []
    for blueprint in blueprints:
        linked_project = find_best_linked_project(blueprint, engineering_projects)
        advisories.append(
            build_app_production_advisory(
                blueprint,
                linked_project,
                None if linked_project is None else research_repo.get(linked_project.id),
                None if linked_project is None else execution_repo.get(linked_project.id),
                None if linked_project is None else experiment_repo.get(linked_project.id),
            )
        )
        if linked_project is not None:
            linkage_notes.append({
                'blueprint_id': blueprint.id,
                'blueprint_name': blueprint.name,
                'linked_project_id': linked_project.id,
                'linked_project_name': linked_project.name,
                'match_score': score_blueprint_project_match(blueprint, linked_project),
            })
    production_portfolio = build_app_production_portfolio_summary(advisories)

    payload = {
        'apps': {
            'count': len(apps),
            'active': len([item for item in apps if item.status.value == 'active']),
        },
        'app_builder': {
            'count': len(blueprints),
        },
        'marketing': {
            'count': len(marketing_projects),
            'active': len([item for item in marketing_projects if item.status.value == 'active']),
        },
        'opportunity_hunter': {
            'scan_count': len(scans),
            'candidate_count': len(opportunity_candidates),
        },
        'investment': {
            'count': len(investments),
            'active': len([item for item in investments if item.status.value in {'active', 'scaling'}]),
        },
        'brain_links': {
            'count': len(brain_links),
            'module_count': len(module_summary),
            'modules': module_summary[:10],
        },
        'software_engineering': {
            'project_count': len(engineering_projects),
            'production_portfolio': production_portfolio.model_dump(mode='json'),
            'linkage_notes': linkage_notes[:10],
        },
        'recent_activity': system_events[:15],
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route='get_master_console_summary_v4',
        returned_count=(len(apps) + len(blueprints) + len(marketing_projects) + len(scans) + len(investments) + len(brain_links) + len(system_events) + len(engineering_projects)),
    )
    return payload
