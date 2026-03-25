from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.data_source_intelligence import CreateDataSourceIntelligenceWorkspaceRequest, UpdateDataSourceIntelligenceStatusRequest, UpsertDataSourceIntelligenceSnapshotRequest
from packages.domain.data_source_intelligence import DataSourceIntelligenceSnapshot, DataSourceIntelligenceStatus, DataSourceIntelligenceWorkspace
from packages.domain.system_events import SystemEventType
from packages.repositories.data_source_intelligence import DataSourceIntelligenceSnapshotRepository, DataSourceIntelligenceWorkspaceRepository
from packages.services.data_source_intelligence import build_data_source_intelligence_summary, review_data_source_intelligence_workspace
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/data-source-intelligence', tags=['source_intelligence'])
telemetry = TelemetryLogger(filepath='var/data_source_intelligence_telemetry.jsonl')

@router.post('/workspaces')
def create_workspace(payload: CreateDataSourceIntelligenceWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = DataSourceIntelligenceWorkspaceRepository(db)
    workspace = DataSourceIntelligenceWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        source_domains=payload.source_domains,
        intelligence_goals=payload.intelligence_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='data_source_intelligence', source_id=saved.id, summary=f'Created data source workspace {saved.name}', metadata={'owner': saved.owner, 'source_domains': saved.source_domains})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')

@router.get('/workspaces')
def list_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in DataSourceIntelligenceWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_workspaces', returned_count=len(payload))
    return payload

@router.post('/workspaces/{workspace_id}/status')
def update_status(workspace_id: str, payload: UpdateDataSourceIntelligenceStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = DataSourceIntelligenceStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = DataSourceIntelligenceWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='data_source_intelligence', source_id=workspace_id, summary=f'Updated data source workspace {saved.name} to {saved.status.value}', metadata={'status': saved.status.value})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')

@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_snapshot(workspace_id: str, payload: UpsertDataSourceIntelligenceSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = DataSourceIntelligenceWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = DataSourceIntelligenceSnapshotRepository(db)
    snapshot = DataSourceIntelligenceSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(db, event_type=SystemEventType.operator_action, source_arm='data_source_intelligence', source_id=workspace_id, summary=f'Updated data source snapshot for {workspace.name}', metadata={'source_quality_score': saved.source_quality_score, 'freshness_confidence_score': saved.freshness_confidence_score})
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_snapshot', workspace_id=workspace_id, source_quality_score=saved.source_quality_score)
    return saved.model_dump(mode='json')

@router.get('/workspaces/{workspace_id}/review')
def get_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace = DataSourceIntelligenceWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_data_source_intelligence_workspace(workspace, DataSourceIntelligenceSnapshotRepository(db).get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')

@router.get('/summary')
def get_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = DataSourceIntelligenceWorkspaceRepository(db).list()
    snapshot_repo = DataSourceIntelligenceSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_data_source_intelligence_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
