from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v33 import app
from packages.storage.orm_company_operator_v2 import CompanyOperatorSnapshotORM, CompanyOperatorWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/company_operator_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    CompanyOperatorWorkspaceORM.metadata.create_all(bind=db_session.engine)
    CompanyOperatorSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_company_operator_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/company-operator/workspaces',
        json={
            'name': 'Company Operator Workspace',
            'owner': 'blake',
            'description': 'Tracks company goals, cadences, KPIs, initiatives, and blockers.',
            'company_names': ['Shortlist', 'Void Signal'],
            'operating_goals': ['grow revenue', 'improve operating discipline'],
            'linked_apps': [],
            'linked_brain_modules': ['reasoning', 'action'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/company-operator/workspaces/{workspace_id}/snapshot',
        json={
            'company_goals': ['reach milestone revenue'],
            'operating_cadences': ['weekly operator review'],
            'kpis': ['weekly revenue', 'active pipeline'],
            'initiatives': ['launch shortlist v1'],
            'owners': ['blake'],
            'blockers': ['limited engineering bandwidth'],
            'decision_execution_links': ['pricing decision linked to launch plan'],
            'opportunities': ['improve operating rhythm'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'operating_health_score': 79,
            'execution_alignment_score': 74,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['operating_health_score'] == 79

    status = client.post(
        f'/api/v1/company-operator/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/company-operator/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/company-operator/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_operating_health_score'] >= 0
    assert summary_payload['average_execution_alignment_score'] >= 0
