from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v27 import app
from packages.storage.orm_reasoning_decision_engine import ReasoningDecisionEngineSnapshotORM, ReasoningDecisionEngineWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/reasoning_decision_engine_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    ReasoningDecisionEngineWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ReasoningDecisionEngineSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_reasoning_decision_engine_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/reasoning-decision-engine/workspaces',
        json={
            'name': 'Reasoning Workspace',
            'owner': 'blake',
            'description': 'Tracks decision synthesis policies and recommendation confidence.',
            'decision_domains': ['vendor selection', 'product prioritization'],
            'reasoning_goals': ['recommendation quality', 'confidence calibration'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'signals'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/reasoning-decision-engine/workspaces/{workspace_id}/snapshot',
        json={
            'reasoning_policies': ['evidence-first reasoning'],
            'recommendation_strategies': ['rank by weighted score'],
            'confidence_rules': ['lower confidence on source conflict'],
            'tradeoff_models': ['cost vs quality model'],
            'risks': ['overconfident ranking'],
            'opportunities': ['better decision synthesis'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'reasoning_quality_score': 78,
            'recommendation_confidence_score': 73,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['reasoning_quality_score'] == 78

    status = client.post(
        f'/api/v1/reasoning-decision-engine/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/reasoning-decision-engine/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/reasoning-decision-engine/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_reasoning_quality_score'] >= 0
    assert summary_payload['average_recommendation_confidence_score'] >= 0
