from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.blueprint_engineering_link import BlueprintEngineeringLinkRepository
from packages.repositories.software_engineering import EngineeringExecutionRepository, EngineeringExperimentRepository, EngineeringProjectRepository, EngineeringResearchRepository
from packages.repositories.system_events import SystemEventRepository
from packages.services.se_app_linking import find_best_linked_project, score_blueprint_project_match
from packages.services.software_engineering_app_production import build_app_production_advisory, build_app_production_portfolio_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v2/software-engineering', tags=['software_engineering_app_production_v3'])
telemetry = TelemetryLogger(filepath='var/software_engineering_telemetry.jsonl')


def resolve_linked_project(blueprint_id: str, db: Session):
    blueprint_repo = AppBlueprintRepository(db)
    project_repo = EngineeringProjectRepository(db)
    link_repo = BlueprintEngineeringLinkRepository(db)
    blueprint = blueprint_repo.get(blueprint_id)
    if blueprint is None:
        return None, None, None, None, None
    persisted_link = link_repo.get_for_blueprint(blueprint_id)
    linked_project = None
    match_score = None
    linkage_reason = None
    linkage_source = 'unlinked'
    if persisted_link is not None:
        linked_project = project_repo.get(persisted_link.engineering_project_id)
        match_score = persisted_link.match_score
        linkage_reason = persisted_link.linkage_reason
        linkage_source = 'persisted'
    else:
        projects = project_repo.list()
        linked_project = find_best_linked_project(blueprint, projects)
        if linked_project is not None:
            match_score = score_blueprint_project_match(blueprint, linked_project)
            linkage_reason = 'auto-matched from blueprint and engineering project signals'
            linkage_source = 'inferred'
    return blueprint, linked_project, match_score, linkage_reason, linkage_source


@router.get('/app-production/summary-v3')
def get_app_production_summary_v3(db: Session = Depends(get_db)) -> dict:
    blueprint_repo = AppBlueprintRepository(db)
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)
    event_repo = SystemEventRepository(db)

    advisories = []
    linkage_notes = []
    persisted_link_count = 0
    inferred_link_count = 0

    for blueprint in blueprint_repo.list():
        _blueprint, linked_project, match_score, linkage_reason, linkage_source = resolve_linked_project(blueprint.id, db)
        if linkage_source == 'persisted':
            persisted_link_count += 1
        elif linkage_source == 'inferred':
            inferred_link_count += 1
        advisory = build_app_production_advisory(
            blueprint,
            linked_project,
            None if linked_project is None else research_repo.get(linked_project.id),
            None if linked_project is None else execution_repo.get(linked_project.id),
            None if linked_project is None else experiment_repo.get(linked_project.id),
        )
        advisories.append(advisory)
        linkage_notes.append({
            'blueprint_id': blueprint.id,
            'blueprint_name': blueprint.name,
            'linked_project_id': None if linked_project is None else linked_project.id,
            'linked_project_name': None if linked_project is None else linked_project.name,
            'match_score': match_score,
            'linkage_reason': linkage_reason,
            'linkage_source': linkage_source,
        })

    portfolio = build_app_production_portfolio_summary(advisories)
    recent_activity = [item.model_dump(mode='json') for item in event_repo.list() if item.source_arm in {'app_builder', 'software_engineering'}]
    payload = {
        'portfolio': portfolio.model_dump(mode='json'),
        'persisted_link_count': persisted_link_count,
        'inferred_link_count': inferred_link_count,
        'advisories': [item.model_dump(mode='json') for item in advisories[:15]],
        'linkage_notes': linkage_notes[:15],
        'recent_activity': recent_activity[:15],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_app_production_summary_v3', returned_count=len(advisories))
    return payload


@router.get('/app-production/blueprint/{blueprint_id}/v3')
def get_blueprint_app_production_advisory_v3(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    research_repo = EngineeringResearchRepository(db)
    execution_repo = EngineeringExecutionRepository(db)
    experiment_repo = EngineeringExperimentRepository(db)
    event_repo = SystemEventRepository(db)

    blueprint, linked_project, match_score, linkage_reason, linkage_source = resolve_linked_project(blueprint_id, db)
    if blueprint is None:
        return {'blueprint': None, 'advisory': None, 'linked_project': None, 'recent_activity': []}

    advisory = build_app_production_advisory(
        blueprint,
        linked_project,
        None if linked_project is None else research_repo.get(linked_project.id),
        None if linked_project is None else execution_repo.get(linked_project.id),
        None if linked_project is None else experiment_repo.get(linked_project.id),
    )
    operator_actions = []
    if advisory.readiness_score >= 75:
        operator_actions.append('Mark blueprint ready for implementation.')
    else:
        operator_actions.extend(advisory.production_priorities[:3])
    if linked_project is None:
        operator_actions.append('Create or link an engineering project for this blueprint.')

    recent_activity = [item.model_dump(mode='json') for item in event_repo.list() if item.source_id in {blueprint_id, None if linked_project is None else linked_project.id}]
    payload = {
        'blueprint': blueprint.model_dump(mode='json'),
        'linked_project': None if linked_project is None else linked_project.model_dump(mode='json'),
        'match_score': match_score,
        'linkage_reason': linkage_reason,
        'linkage_source': linkage_source,
        'advisory': advisory.model_dump(mode='json'),
        'operator_actions': operator_actions[:5],
        'recent_activity': recent_activity[:10],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_blueprint_app_production_advisory_v3', blueprint_id=blueprint_id)
    return payload
