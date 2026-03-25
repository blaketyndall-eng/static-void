from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v17 import app
from packages.storage.orm_system_events import SystemEventRecordORM
from packages.storage.orm_verticalization import VerticalPacksSnapshotORM, VerticalPacksWorkspaceORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/vertical_packs_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    VerticalPacksWorkspaceORM.metadata.create_all(bind=db_session.engine)
    VerticalPacksSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_vertical_packs_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/vertical-packs/workspaces',
        json={
            'name': 'Software Procurement Pack',
            'owner': 'blake',
            'description': 'Builds reusable pack assets for software procurement workflows.',
            'industries': ['software', 'procurement'],
            'pack_goals': ['pack templates', 'scoring logic'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'evaluation'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/vertical-packs/workspaces/{workspace_id}/snapshot',
        json={
            'pack_templates': ['vendor evaluation template'],
            'scoring_models': ['weighted procurement score'],
            'domain_playbooks': ['security review playbook'],
            'knowledge_assets': ['procurement glossary'],
            'risks': ['overgeneralized template'],
            'opportunities': ['reuse scoring model across packs'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'pack_quality_score': 73,
            'adaptation_readiness_score': 69,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['pack_quality_score'] == 73

    status = client.post(
        f'/api/v1/vertical-packs/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/vertical-packs/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/vertical-packs/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_pack_quality_score'] >= 0
    assert summary_payload['average_adaptation_readiness_score'] >= 0
