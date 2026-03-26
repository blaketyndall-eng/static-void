from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.feedback_outcome_scoring import (
    CreateFeedbackOutcomeScoringWorkspaceRequest,
    UpdateFeedbackOutcomeScoringStatusRequest,
    UpsertFeedbackOutcomeScoringSnapshotRequest,
)
from packages.domain.feedback_outcome_scoring import (
    FeedbackOutcomeScoringSnapshot,
    FeedbackOutcomeScoringStatus,
    FeedbackOutcomeScoringWorkspace,
)
from packages.domain.system_events import SystemEventType
from packages.repositories.feedback_outcome_scoring import (
    FeedbackOutcomeScoringSnapshotRepository,
    FeedbackOutcomeScoringWorkspaceRepository,
)
from packages.services.feedback_outcome_scoring import (
    build_feedback_outcome_scoring_summary,
    review_feedback_outcome_scoring_workspace,
)
from packages.services.system_event_helpers import record_system_event
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/feedback-outcome-scoring', tags=['feedback_outcome_scoring'])
telemetry = TelemetryLogger(filepath='var/feedback_outcome_scoring_telemetry.jsonl')


@router.post('/workspaces')
def create_feedback_workspace(payload: CreateFeedbackOutcomeScoringWorkspaceRequest, db: Session = Depends(get_db)) -> dict:
    repo = FeedbackOutcomeScoringWorkspaceRepository(db)
    workspace = FeedbackOutcomeScoringWorkspace(
        name=payload.name,
        owner=payload.owner,
        description=payload.description,
        outcome_domains=payload.outcome_domains,
        scoring_goals=payload.scoring_goals,
        linked_apps=payload.linked_apps,
        linked_brain_modules=payload.linked_brain_modules,
    )
    saved = repo.create(workspace)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='feedback_outcome_scoring',
        source_id=saved.id,
        summary=f'Created feedback workspace {saved.name}',
        metadata={'owner': saved.owner, 'outcome_domains': saved.outcome_domains},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_feedback_workspace', workspace_id=saved.id)
    return saved.model_dump(mode='json')


@router.get('/workspaces')
def list_feedback_workspaces(db: Session = Depends(get_db)) -> list[dict]:
    payload = [item.model_dump(mode='json') for item in FeedbackOutcomeScoringWorkspaceRepository(db).list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_feedback_workspaces', returned_count=len(payload))
    return payload


@router.post('/workspaces/{workspace_id}/status')
def update_feedback_status(workspace_id: str, payload: UpdateFeedbackOutcomeScoringStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = FeedbackOutcomeScoringStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = FeedbackOutcomeScoringWorkspaceRepository(db)
    saved = repo.update_status(workspace_id, status)
    if saved is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='feedback_outcome_scoring',
        source_id=workspace_id,
        summary=f'Updated feedback workspace {saved.name} to {saved.status.value}',
        metadata={'status': saved.status.value},
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_feedback_status', workspace_id=workspace_id, status=saved.status.value)
    return saved.model_dump(mode='json')


@router.post('/workspaces/{workspace_id}/snapshot')
def upsert_feedback_snapshot(workspace_id: str, payload: UpsertFeedbackOutcomeScoringSnapshotRequest, db: Session = Depends(get_db)) -> dict:
    workspace = FeedbackOutcomeScoringWorkspaceRepository(db).get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    repo = FeedbackOutcomeScoringSnapshotRepository(db)
    snapshot = FeedbackOutcomeScoringSnapshot(workspace_id=workspace_id, **payload.model_dump())
    saved = repo.upsert(snapshot)
    record_system_event(
        db,
        event_type=SystemEventType.operator_action,
        source_arm='feedback_outcome_scoring',
        source_id=workspace_id,
        summary=f'Updated feedback snapshot for {workspace.name}',
        metadata={
            'outcome_quality_score': saved.outcome_quality_score,
            'feedback_readiness_score': saved.feedback_readiness_score,
            'outcome_reviews': saved.outcome_reviews,
        },
    )
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_feedback_snapshot', workspace_id=workspace_id, outcome_quality_score=saved.outcome_quality_score)
    return saved.model_dump(mode='json')


@router.get('/workspaces/{workspace_id}/review')
def get_feedback_review(workspace_id: str, db: Session = Depends(get_db)) -> dict:
    workspace_repo = FeedbackOutcomeScoringWorkspaceRepository(db)
    snapshot_repo = FeedbackOutcomeScoringSnapshotRepository(db)
    workspace = workspace_repo.get(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail='workspace not found')
    review = review_feedback_outcome_scoring_workspace(workspace, snapshot_repo.get(workspace_id))
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_feedback_review', workspace_id=workspace_id, review_score=review.review_score)
    return review.model_dump(mode='json')


@router.get('/summary')
def get_feedback_summary(db: Session = Depends(get_db)) -> dict:
    workspaces = FeedbackOutcomeScoringWorkspaceRepository(db).list()
    snapshot_repo = FeedbackOutcomeScoringSnapshotRepository(db)
    snapshots = {workspace.id: snapshot_repo.get(workspace.id) for workspace in workspaces}
    snapshots = {key: value for key, value in snapshots.items() if value is not None}
    summary = build_feedback_outcome_scoring_summary(workspaces, snapshots)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_feedback_summary', returned_count=summary.workspace_count)
    return summary.model_dump(mode='json')
