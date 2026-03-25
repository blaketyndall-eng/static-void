from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v16 import app
from packages.storage.orm_decision_memory import DecisionMemorySnapshotORM, DecisionMemoryWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/decision_memory_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    DecisionMemoryWorkspaceORM.metadata.create_all(bind=db_session.engine)
    DecisionMemorySnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_decision_memory_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/decision-memory/workspaces',
        json={
            'name': 'Decision Memory Workspace',
            'owner': 'blake',
            'description': 'Tracks decisions, outcomes, and regret patterns.',
            'memory_domains': ['vendor decisions', 'product decisions'],
            'review_goals': ['calibration', 'reuse'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'evaluation'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/decision-memory/workspaces/{workspace_id}/snapshot',
        json={
            'captured_decisions': ['vendor shortlist approved'],
            'outcome_reviews': ['6 month ROI review'],
            'regret_patterns': ['late stakeholder alignment'],
            'reuse_candidates': ['security checklist reuse'],
            'risks': ['memory gaps'],
            'opportunities': ['reuse proven playbooks'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'memory_quality_score': 72,
            'calibration_score': 65,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['memory_quality_score'] == 72

    status = client.post(
        f'/api/v1/decision-memory/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/decision-memory/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/decision-memory/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_memory_quality_score'] >= 0
    assert summary_payload['average_calibration_score'] >= 0
