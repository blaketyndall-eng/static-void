from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v31 import app
from packages.storage.orm_feedback_outcome_scoring import FeedbackOutcomeScoringSnapshotORM, FeedbackOutcomeScoringWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/feedback_outcome_scoring_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    FeedbackOutcomeScoringWorkspaceORM.metadata.create_all(bind=db_session.engine)
    FeedbackOutcomeScoringSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_feedback_outcome_scoring_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/feedback-outcome-scoring/workspaces',
        json={
            'name': 'Feedback Workspace',
            'owner': 'blake',
            'description': 'Tracks outcome reviews, prediction checks, and usefulness scoring.',
            'outcome_domains': ['vendor decisions', 'product bets'],
            'scoring_goals': ['outcome quality', 'learning loops'],
            'linked_apps': [],
            'linked_brain_modules': ['reasoning', 'memory'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/feedback-outcome-scoring/workspaces/{workspace_id}/snapshot',
        json={
            'outcome_reviews': ['quarterly decision review'],
            'prediction_checks': ['predicted savings vs actual'],
            'usefulness_scores': ['brief usefulness score'],
            'regret_signals': ['would not repeat vendor choice'],
            'risks': ['weak feedback loop'],
            'opportunities': ['improve learning from outcomes'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'outcome_quality_score': 81,
            'feedback_readiness_score': 76,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['outcome_quality_score'] == 81

    status = client.post(
        f'/api/v1/feedback-outcome-scoring/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/feedback-outcome-scoring/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/feedback-outcome-scoring/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_outcome_quality_score'] >= 0
    assert summary_payload['average_feedback_readiness_score'] >= 0
