from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v36 import app
from packages.storage.orm_system_events import SystemEventRecordORM
from packages.storage.orm_venture_builder import VentureBuilderSnapshotORM, VentureBuilderWorkspaceORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/venture_builder_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    VentureBuilderWorkspaceORM.metadata.create_all(bind=db_session.engine)
    VentureBuilderSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_vb_smoke() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/venture-builder/workspaces',
        json={
            'name': 'VB Workspace',
            'owner': 'blake',
            'description': 'Tracks launch planning and validation.',
            'venture_ideas': ['decision studio'],
            'thesis_points': ['clear buyer pain'],
            'linked_apps': ['shortlist'],
            'linked_modules': ['image_studio', 'company_operator'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/venture-builder/workspaces/{workspace_id}/snapshot',
        json={
            'stages': ['idea', 'validation'],
            'launch_milestones': ['landing page', 'pilot'],
            'owners': ['blake'],
            'dependencies': ['design ready'],
            'blockers': ['time'],
            'go_no_go_evidence': ['customer calls'],
            'decision_launch_links': ['approval linked to sprint'],
            'opportunities': ['strong wedge'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'launch_readiness_score': 76,
            'venture_confidence_score': 79,
        },
    )
    assert snapshot.status_code == 200

    status = client.post(
        f'/api/v1/venture-builder/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200

    review = client.get(f'/api/v1/venture-builder/workspaces/{workspace_id}/review')
    assert review.status_code == 200

    summary = client.get('/api/v1/venture-builder/summary')
    assert summary.status_code == 200
    assert summary.json()['workspace_count'] >= 1
