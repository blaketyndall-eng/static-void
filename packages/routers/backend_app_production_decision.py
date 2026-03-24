from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.app_production_decision import UpsertAppProductionDecisionRequest
from packages.domain.app_production_decision import AppProductionDecision, AppProductionDecisionState
from packages.domain.system_events import SystemEventType
from packages.repositories.app_builder import AppBlueprintRepository
from packages.repositories.app_production_decision import AppProductionDecisionRepository
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v2/app-builder', tags=['app_production_decision'])
telemetry = TelemetryLogger(filepath='var/app_builder_telemetry.jsonl')


@router.post('/blueprints/{blueprint_id}/production-decision')
def upsert_app_production_decision(blueprint_id: str, payload: UpsertAppProductionDecisionRequest, db: Session = Depends(get_db)) -> dict:
    blueprint = AppBlueprintRepository(db).get(blueprint_id)
    if blueprint is None:
        raise HTTPException(status_code=404, detail='blueprint not found')
    try:
        decision_state = AppProductionDecisionState(payload.decision)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid decision') from exc

    repo = AppProductionDecisionRepository(db)
    saved = repo.upsert(
        AppProductionDecision(
            blueprint_id=blueprint_id,
            decision=decision_state,
            rationale=payload.rationale,
            action_items=payload.action_items,
            advisory_score=payload.advisory_score,
        )
    )
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='app_builder',
        source_id=blueprint_id,
        summary=f'Production decision for {blueprint.name}: {saved.decision.value}',
        metadata={
            'decision': saved.decision.value,
            'advisory_score': saved.advisory_score,
            'action_items': saved.action_items,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_app_production_decision', blueprint_id=blueprint_id, decision=saved.decision.value)
    return saved.model_dump(mode='json')


@router.get('/blueprints/{blueprint_id}/production-decision')
def get_app_production_decision(blueprint_id: str, db: Session = Depends(get_db)) -> dict:
    repo = AppProductionDecisionRepository(db)
    item = repo.get_for_blueprint(blueprint_id)
    if item is None:
        return {'decision': None}
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_app_production_decision', blueprint_id=blueprint_id)
    return {'decision': item.model_dump(mode='json')}
