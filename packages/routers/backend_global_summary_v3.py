from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.brain_links import BrainLinkRepository
from packages.repositories.opportunity_hunter import OpportunityCandidateRepository, OpportunityScanRepository
from packages.repositories.software_engineering import (
    EngineeringExecutionRepository,
    EngineeringExperimentRepository,
    EngineeringProjectRepository,
    EngineeringResearchRepository,
)
from packages.repositories.system_events import SystemEventRepository
from packages.services.se_app_linking import find_best_linked_project
from packages.services.software_engineering_app_production import (
    build_app_production_advisory,
    build_app_production_portfolio_summary,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/global', tags=['global_summary_v3'])
telemetry = TelemetryLogger(filepath='var/system_events_telemetry.jsonl')


@router.get('/summary-v3')
def get_global_system_summary_v3(db: Session = Depends(get_db)) -> dict:
    brain_links = BrainLinkRepository(db).list()
    module_summary = [item.model_dump(mode='json') for item in BrainLinkRepository(db).summarize_modules()]
    events = [item.model_dump(mode='json') for item in SystemEventRepository(db).list()]
    scans = OpportunityScanRepository(db).list()
    opp_repo = OpportunityCandidateRepository(db)
    candidates = []
    for scan in scans:
        candidates.extend(opp_repo.list_for_scan(scan.id))

    blueprints = AppBlueprintRepository(db).list()
    engineering_projects = EngineeringProjectRepository(db).list()
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)
    advisories = []
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
    production_portfolio = build_app_production_portfolio_summary(advisories)

    payload = {
        'brain_links': {
            'count': len(brain_links),
            'modules': module_summary[:10],
        },
        'system_events': {
            'count': len(events),
            'recent': events[:15],
        },
        'opportunity_hunter': {
            'scan_count': len(scans),
            'candidate_count': len(candidates),
        },
        'software_engineering': {
            'project_count': len(engineering_projects),
            'production_portfolio': production_portfolio.model_dump(mode='json'),
        },
    }
    emit_view_event(
        telemetry,
        API_REQUEST_COMPLETED,
        route='get_global_system_summary_v3',
        returned_count=(len(brain_links) + len(events) + len(candidates) + len(engineering_projects)),
    )
    return payload
