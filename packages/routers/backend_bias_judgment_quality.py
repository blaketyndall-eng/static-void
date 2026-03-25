from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.bias_judgment_quality import (
    CreateBiasJudgmentQualityWorkspaceRequest,
    UpdateBiasJudgmentQualityStatusRequest,
    UpsertBiasJudgmentQualitySnapshotRequest,
)
from packages.domain.bias_judgment_quality import (
    BiasJudgmentQualitySnapshot,
    BiasJudgmentQualityStatus,
    BiasJudgmentQualityWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.bias_judgment_quality import (
    BiasJudgmentQualitySnapshotRepository,
    BiasJudgmentQualityWorkspaceRepository,
)
from packages.services.bias_judgment_quality import (
    build_bias_judgment_quality_summary,
    review_bias_judgment_quality_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/bias-judgment-quality', tags=['bias_judgment_quality'])
telemetry = TelemetryLogger(filepath='var/bias_judgment_quality_telemetry.jsonl')


@router.post('/workspaces')
def create_bias_workspace(payload: CreateBiasJudgmentQualityWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = BiasJudgmentQualityWorkspaceRepository(db)
    workspace = BiasJudgmentQualityWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        judgment_domains=payload.judgment_domains,
        quality_goals=payload.quality_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='bias_judgment_quality',
        source_id=saved.id,
        summary=f'Created bias workspace {saved.name}',
        metadata={'owner': saved.owner, 'judgment_domains': saved.judgment_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_bias_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_bias_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in BiasJudgmentQualityWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_bias_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_bias_status(workspace_id: str, payload: UpdateBiasJudgmentQualityStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = BiasJudgmentQualityStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = BiasJudgmentQualityWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='bias_judgment_quality',
        source_id=workspace_id,
        summary=f'Updated bias workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_bias_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_bias_snapshot(workspace_id: str, payload: UpsertBiasJudgmentQualitySnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = BiasJudgmentQualityWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = BiasJudgmentQualitySnapshotRepository(db)
    snapshot = BiasJudgmentQualitySnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='bias_judgment_quality',
        source_id=workspace_id,
        summary=f'Updated bias snapshot for {workspace.name}',
        metadata={
            'judgment_quality_score': saved.judgment_quality_score,
            'calibration_readiness_score': saved.calibration_readiness_score,
            'bias_checks': saved.bias_checks,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_bias_snapshot', workspace_id=workspace_id, judgment_quality_score=saved.judgment_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_bias_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = BiasJudgmentQualityWorkspaceRepository(db)
    snapshot_repo = BiasJudgmentQualitySnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_bias_judgment_quality_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_bias_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_bias_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = BiasJudgmentQualityWorkspaceRepository(db).list()
    snapshot_repo = BiasJudgmentQualitySnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_bias_judgment_quality_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_bias_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
