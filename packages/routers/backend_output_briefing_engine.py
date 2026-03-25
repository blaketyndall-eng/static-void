from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.output_briefing_engine import (
    CreateOutputBriefingEngineWorkspaceRequest,
    UpdateOutputBriefingEngineStatusRequest,
    UpsertOutputBriefingEngineSnapshotRequest,
)
from packages.domain.output_briefing_engine import (
    OutputBriefingEngineSnapshot,
    OutputBriefingEngineStatus,
    OutputBriefingEngineWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.output_briefing_engine import (
    OutputBriefingEngineSnapshotRepository,
    OutputBriefingEngineWorkspaceRepository,
)
from packages.services.output_briefing_engine import (
    build_output_briefing_engine_summary,
    review_output_briefing_engine_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/output-briefing-engine', tags=['output_briefing_engine'])
telemetry = TelemetryLogger(filepath='var/output_briefing_engine_telemetry.jsonl')


@router.post('/workspaces')
def create_output_workspace(payload: CreateOutputBriefingEngineWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = OutputBriefingEngineWorkspaceRepository(db)
    workspace = OutputBriefingEngineWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        briefing_domains=payload.briefing_domains,
        output_goals=payload.output_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='output_briefing_engine',
        source_id=saved.id,
        summary=f'Created output workspace {saved.name}',
        metadata={'owner': saved.owner, 'briefing_domains': saved.briefing_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_output_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_output_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in OutputBriefingEngineWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_output_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_output_status(workspace_id: str, payload: UpdateOutputBriefingEngineStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = OutputBriefingEngineStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = OutputBriefingEngineWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='output_briefing_engine',
        source_id=workspace_id,
        summary=f'Updated output workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_output_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_output_snapshot(workspace_id: str, payload: UpsertOutputBriefingEngineSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = OutputBriefingEngineWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = OutputBriefingEngineSnapshotRepository(db)
    snapshot = OutputBriefingEngineSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='output_briefing_engine',
        source_id=workspace_id,
        summary=f'Updated output snapshot for {workspace.name}',
        metadata={
            'output_quality_score': saved.output_quality_score,
            'briefing_readiness_score': saved.briefing_readiness_score,
            'briefing_templates': saved.briefing_templates,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_output_snapshot', workspace_id=workspace_id, output_quality_score=saved.output_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_output_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = OutputBriefingEngineWorkspaceRepository(db)
    snapshot_repo = OutputBriefingEngineSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_output_briefing_engine_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_output_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_output_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = OutputBriefingEngineWorkspaceRepository(db).list()
    snapshot_repo = OutputBriefingEngineSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_output_briefing_engine_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_output_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
