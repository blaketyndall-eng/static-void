from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.company_operator import (
    CreateCompanyOperatorWorkspaceRequest,
    UpdateCompanyOperatorStatusRequest,
    UpsertCompanyOperatorSnapshotRequest,
)
from packages.domain.company_operator import CompanyOperatorSnapshot, CompanyOperatorStatus, CompanyOperatorWorkspace
from packages.domain.system_events import SystemEventType
from packages.repositories.company_operator import CompanyOperatorSnapshotRepository, CompanyOperatorWorkspaceRepository
from packages.services.company_operator import build_company_operator_summary, review_company_operator_workspace
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/company-operator', tags=['company_operator'])
telemetry = TelemetryLogger(filepath='var/company_operator_telemetry.jsonl')


@router.post('/workspaces')
def create_company_operator_workspace(payload: CreateCompanyOperatorWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = CompanyOperatorWorkspaceRepository(db)
    workspace = CompanyOperatorWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        company_names=payload.company_names,
        operating_goals=payload.operating_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='company_operator',
        source_id=saved.id,
        summary=f'Created company operator workspace {saved.name}',
        metadata={'owner': saved.owner, 'company_names': saved.company_names},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_company_operator_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_company_operator_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in CompanyOperatorWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_company_operator_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_company_operator_status(workspace_id: str, payload: UpdateCompanyOperatorStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = CompanyOperatorStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = CompanyOperatorWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='company_operator',
        source_id=workspace_id,
        summary=f'Updated company operator workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_company_operator_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_company_operator_snapshot(workspace_id: str, payload: UpsertCompanyOperatorSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = CompanyOperatorWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = CompanyOperatorSnapshotRepository(db)
    snapshot = CompanyOperatorSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='company_operator',
        source_id=workspace_id,
        summary=f'Updated company operator snapshot for {workspace.name}',
        metadata={
            'operating_health_score': saved.operating_health_score,
            'execution_alignment_score': saved.execution_alignment_score,
            'kpis': saved.kpis,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_company_operator_snapshot', workspace_id=workspace_id, operating_health_score=saved.operating_health_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_company_operator_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = CompanyOperatorWorkspaceRepository(db)
    snapshot_repo = CompanyOperatorSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_company_operator_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_company_operator_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_company_operator_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = CompanyOperatorWorkspaceRepository(db).list()
    snapshot_repo = CompanyOperatorSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_company_operator_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_company_operator_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
