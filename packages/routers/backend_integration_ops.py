from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.integrations_automation import CreateIntegrationsAutomationWorkspaceRequest, UpdateIntegrationsAutomationStatusRequest, UpsertIntegrationsAutomationSnapshotRequest
from packages.domain.integrations_automation import IntegrationsAutomationSnapshot, IntegrationsAutomationStatus, IntegrationsAutomationWorkspace
from packages.domain.system_events import SystemEventType
from packages.repositories.integrations_automation import IntegrationsAutomationSnapshotRepository, IntegrationsAutomationWorkspaceRepository
from packages.services.integrations_automation import build_integrations_automation_summary, review_integrations_automation_workspace
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/integrations-automation', tags=['integration_ops'])
telemetry = TelemetryLogger(filepath='var/integrations_automation_telemetry.jsonl')

@router.post('/workspaces')
def create_workspace(payload: CreateIntegrationsAutomationWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = IntegrationsAutomationWorkspaceRepository(db)
    workspace = IntegrationsAutomationWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        integration_targets=payload.integration_targets,
        automation_goals=payload.automation_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='integrations_automation', source_id=saved.id, summary=f'Created integrations workspace {saved.name}', metadata={'owner': saved.owner, 'integration_targets': saved.integration_targets})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')

@router.get('/workspaces')
def list_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in IntegrationsAutomationWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_workspaces', returned_count=len(payload))
    return payload

@router.post('/workspaces/{workspace_id}/status')
def update_status(workspace_id: str, payload: UpdateIntegrationsAutomationStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = IntegrationsAutomationStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = IntegrationsAutomationWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='integrations_automation', source_id=workspace_id, summary=f'Updated integrations workspace {saved.name} to {saved.status.value}', metadata={'status': saved.status.value})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')

@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_snapshot(workspace_id: str, payload: UpsertIntegrationsAutomationSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = IntegrationsAutomationWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = IntegrationsAutomationSnapshotRepository(db)
    snapshot = IntegrationsAutomationSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='integrations_automation', source_id=workspace_id, summary=f'Updated integrations snapshot for {workspace.name}', metadata={'integration_health_score': saved.integration_health_score, 'automation_reliability_score': saved.automation_reliability_score})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_snapshot', workspace_id=workspace_id, integration_health_score=saved.integration_health_score)
    return saved.model_dump(mode='json')

@router.get('/workspaces/{workspace_id}/review')
def get_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace = IntegrationsAutomationWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_integrations_automation_workspace(workspace, IntegrationsAutomationSnapshotRepository(db).get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')

@router.get('/summary')
def get_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = IntegrationsAutomationWorkspaceRepository(db).list()
    snapshot_repo = IntegrationsAutomationSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_integrations_automation_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
