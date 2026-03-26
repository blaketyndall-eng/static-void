from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.image_studio import (
    CreateImageStudioRenderJobRequest,
    CreateImageStudioWorkspaceRequest,
    UpdateImageStudioStatusRequest,
    UpsertImageStudioSnapshotRequest,
)
from packages.domain.image_studio import (
    ImageStudioRenderJob,
    ImageStudioSnapshot,
    ImageStudioStatus,
    ImageStudioWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.image_studio import (
    ImageStudioRenderJobRepository,
    ImageStudioSnapshotRepository,
    ImageStudioWorkspaceRepository,
)
from packages.services.image_studio import (
    build_image_studio_summary,
    build_render_job_summary,
    review_image_studio_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/image-studio', tags=['image_studio'])
telemetry = TelemetryLogger(filepath='var/image_studio_telemetry.jsonl')


@router.post('/workspaces')
def create_image_studio_workspace(payload: CreateImageStudioWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = ImageStudioWorkspaceRepository(db)
    workspace = ImageStudioWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        creative_domains=payload.creative_domains,
        output_goals=payload.output_goals,
        linked_apps=payload.linked_apps,
        linked_modules=payload.linked_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='image_studio',
        source_id=saved.id,
        summary=f'Created image studio workspace {saved.name}',
        metadata={'owner': saved.owner, 'creative_domains': saved.creative_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_image_studio_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_image_studio_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in ImageStudioWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_image_studio_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_image_studio_status(workspace_id: str, payload: UpdateImageStudioStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ImageStudioStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = ImageStudioWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='image_studio',
        source_id=workspace_id,
        summary=f'Updated image studio workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_image_studio_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_image_studio_snapshot(workspace_id: str, payload: UpsertImageStudioSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ImageStudioWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ImageStudioSnapshotRepository(db)
    snapshot = ImageStudioSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='image_studio',
        source_id=workspace_id,
        summary=f'Updated image studio snapshot for {workspace.name}',
        metadata={
            'creative_reliability_score': saved.creative_reliability_score,
            'deployment_readiness_score': saved.deployment_readiness_score,
            'generation_modes': saved.generation_modes,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_image_studio_snapshot', workspace_id=workspace_id, creative_reliability_score=saved.creative_reliability_score)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/jobs')
def create_image_render_job(workspace_id: str, payload: CreateImageStudioRenderJobRequest, db: Session = Depends(get_db)) -> dict:
    workspace = ImageStudioWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = ImageStudioRenderJobRepository(db)
    job = ImageStudioRenderJob(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.create(job)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='image_studio',
        source_id=saved.id,
        summary=f'Created image render job for {workspace.name}',
        metadata={'mode': saved.mode, 'model_name': saved.model_name, 'status': saved.status},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_image_render_job', workspace_id=workspace_id, job_id=saved.id, mode=saved.mode)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/jobs')
def list_image_render_jobs(workspace_id: str, db: Session = Depends(get_db)) -> list[dict]:
    workspace = ImageStudioWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    jobs = [item.model_dump(mode='json') for item in ImageStudioRenderJobRepository(db).list_for_workspace(workspace_id)]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_image_render_jobs', workspace_id=workspace_id, returned_count=len(jobs))
    return jobs


@router.get('/workspaces/{workspace_id}/jobs/summary')
def get_image_render_job_summary(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace = ImageStudioWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    jobs = ImageStudioRenderJobRepository(db).list_for_workspace(workspace_id)
    summary = build_render_job_summary(workspace_id, jobs)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_image_render_job_summary', workspace_id=workspace_id, returned_count=len(jobs))
    return summary.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_image_studio_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = ImageStudioWorkspaceRepository(db)
    snapshot_repo = ImageStudioSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_image_studio_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_image_studio_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_image_studio_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = ImageStudioWorkspaceRepository(db).list()
    snapshot_repo = ImageStudioSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_image_studio_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_image_studio_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
