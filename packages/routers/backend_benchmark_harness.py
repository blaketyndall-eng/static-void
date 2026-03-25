from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.benchmark_harness import (
    CreateBenchmarkHarnessWorkspaceRequest,
    UpdateBenchmarkHarnessStatusRequest,
    UpsertBenchmarkHarnessSnapshotRequest,
)
from packages.domain.benchmark_harness import (
    BenchmarkHarnessSnapshot,
    BenchmarkHarnessStatus,
    BenchmarkHarnessWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.benchmark_harness import (
    BenchmarkHarnessSnapshotRepository,
    BenchmarkHarnessWorkspaceRepository,
)
from packages.services.benchmark_harness import (
    build_benchmark_harness_summary,
    review_benchmark_harness_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/benchmark-harness', tags=['benchmark_harness'])
telemetry = TelemetryLogger(filepath='var/benchmark_harness_telemetry.jsonl')


@router.post('/workspaces')
def create_benchmark_workspace(payload: CreateBenchmarkHarnessWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = BenchmarkHarnessWorkspaceRepository(db)
    workspace = BenchmarkHarnessWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        benchmark_domains=payload.benchmark_domains,
        benchmark_goals=payload.benchmark_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='benchmark_harness',
        source_id=saved.id,
        summary=f'Created benchmark workspace {saved.name}',
        metadata={'owner': saved.owner, 'benchmark_domains': saved.benchmark_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_benchmark_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_benchmark_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in BenchmarkHarnessWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_benchmark_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_benchmark_status(workspace_id: str, payload: UpdateBenchmarkHarnessStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = BenchmarkHarnessStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = BenchmarkHarnessWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='benchmark_harness',
        source_id=workspace_id,
        summary=f'Updated benchmark workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_benchmark_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_benchmark_snapshot(workspace_id: str, payload: UpsertBenchmarkHarnessSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = BenchmarkHarnessWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = BenchmarkHarnessSnapshotRepository(db)
    snapshot = BenchmarkHarnessSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='benchmark_harness',
        source_id=workspace_id,
        summary=f'Updated benchmark snapshot for {workspace.name}',
        metadata={
            'benchmark_quality_score': saved.benchmark_quality_score,
            'harness_readiness_score': saved.harness_readiness_score,
            'benchmark_suites': saved.benchmark_suites,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_benchmark_snapshot', workspace_id=workspace_id, benchmark_quality_score=saved.benchmark_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_benchmark_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = BenchmarkHarnessWorkspaceRepository(db)
    snapshot_repo = BenchmarkHarnessSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_benchmark_harness_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_benchmark_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_benchmark_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = BenchmarkHarnessWorkspaceRepository(db).list()
    snapshot_repo = BenchmarkHarnessSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_benchmark_harness_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_benchmark_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
