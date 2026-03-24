from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.blueprint_engineering_link import UpsertBlueprintEngineeringLinkRequest
from packages.domain.blueprint_engineering_link import BlueprintEngineeringLink
from packages.domain.system_events import SystemEventType
from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.blueprint_engineering_link import BlueprintEngineeringLinkRepository
from packages.repositories.software_engineering import EngineeringProjectRepository
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v2/app-builder', tags=['blueprint_engineering_link'])
telemetry = TelemetryLogger(filepath='var/app_builder_telemetry.jsonl')


@router.post('/blueprints/{blueprint_id}/engineering-link')
def upsert_blueprint_engineering_link(blueprint_id: str, payload: UpsertBlueprintEngineeringLinkRequest, db: Session = Depends(get_db)) -> dict:
    blueprint = AppBlueprintRepository(db).get(blueprint_id)
    if blueprint is None:
        raise HTTPException(status_code=404, detail='blueprint not found')
    project = EngineeringProjectRepository(db).get(payload.engineering_project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='engineering project not found')

    repo = BlueprintEngineeringLinkRepository(db)
    saved = repo.upsert(
        BlueprintEngineeringLink(
            blueprint_id=blueprint_id,
            engineering_project_id=payload.engineering_project_id,
            match_score=payload.match_score,
            linkage_reason=payload.linkage_reason,
            is_manual_override=payload.is_manual_override,
        )
    )
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='app_builder',
        source_id=blueprint_id,
        summary=f'Linked blueprint {blueprint.name} to engineering project {project.name}',
        metadata={
            'engineering_project_id': project.id,
            'match_score': saved.match_score,
            'is_manual_override': saved.is_manual_override,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_blueprint_engineering_link', blueprint_id=blueprint_id, engineering_project_id=project.id)
    return saved.model_dump(mode='json')


@router.get('/blueprints/{blueprint_id}/engineering-link')
def get_blueprint_engineering_link(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    repo = BlueprintEngineeringLinkRepository(db)
    link = repo.get_for_blueprint(blueprint_id)
    if link is None:
        return {'link': None}
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_blueprint_engineering_link', blueprint_id=blueprint_id)
    return {'link': link.model_dump(mode='json')}
