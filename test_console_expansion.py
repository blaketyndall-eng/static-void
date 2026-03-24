from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v11 import app
from packages.storage.orm_console_expansion import ConsoleArmSnapshotORM, ConsoleArmWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/console_expansion_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    ConsoleArmWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ConsoleArmSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_console_expansion_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/console-expansion/workspaces',
        json={
            'arm_type': 'ai_governance',
            'name': 'AI Governance Lab',
            'owner': 'blake',
            'description': 'Build governance workflows and model review systems.',
            'goals': ['benchmarks', 'monitoring', 'policy'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'evaluation'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/console-expansion/workspaces/{workspace_id}/snapshot',
        json={
            'focus_areas': ['evaluation', 'policy'],
            'active_tracks': ['benchmark registry', 'risk review'],
            'risks': ['policy drift'],
            'opportunities': ['shared evaluation layer'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'maturity_score': 61,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['maturity_score'] == 61

    status = client.post(
        f'/api/v1/console-expansion/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/console-expansion/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/console-expansion/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['by_arm_type']['ai_governance'] >= 1
