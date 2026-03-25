from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.research_lab import (
    CreateResearchLabWorkspaceRequest,
    UpdateResearchLabStatusRequest,
    UpsertResearchLabSnapshotRequest,
)
from packages.domain.research_lab import (
    ResearchLabSnapshot,
    ResearchLabStatus,
    ResearchLabWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.research_lab import (
    ResearchLabSnapshotRepository,
    ResearchLabWorkspaceRepository,
)
from packages.services.research_lab import (
    build_research_lab_summary,
    review_research_lab_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/research-lab', tags=['research_lab'])
telemetry = TelemetryLogger(filepath='var/research_lab_telemetry.jsonl')


@router.post('/workspaces')
def create_research_lab_workspace(payload: CreateResearchLabWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = ResearchLabWorkspaceRepository(db)
    workspace = ResearchLabWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        experiment_domains=payload.experiment_domains,
        benchmark_targets=payload.benchmark_targets,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='research_lab',
        source_id=saved.id,
        summary=f'Created research lab workspace {saved.name}',
        metadata={'owner': saved.owner, 'experiment_domains': saved.experiment_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_research_lab_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_research_lab_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in ResearchLabWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_research_lab_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_research_lab_status(workspace_id: str, payload: UpdateResearchLabStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ResearchLabStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = ResearchLabWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='research_lab',
        source_id=workspace_id,
        summary=f'Updated research lab workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_research_lab_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_research_lab_snapshot(workspace_id: str, payload: UpsertResearchLabSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ResearchLabWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ResearchLabSnapshotRepository(db)
    snapshot = ResearchLabSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='research_lab',
        source_id=workspace_id,
        summary=f'Updated research lab snapshot for {workspace.name}',
        metadata={
            'experiment_quality_score': saved.experiment_quality_score,
            'benchmark_confidence_score': saved.benchmark_confidence_score,
            'active_experiments': saved.active_experiments,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_research_lab_snapshot', workspace_id=workspace_id, experiment_quality_score=saved.experiment_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_research_lab_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = ResearchLabWorkspaceRepository(db)
    snapshot_repo = ResearchLabSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_research_lab_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_research_lab_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_research_lab_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = ResearchLabWorkspaceRepository(db).list()
    snapshot_repo = ResearchLabSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_research_lab_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_research_lab_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
