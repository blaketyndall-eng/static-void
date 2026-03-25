from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v28 import app
from packages.storage.orm_output_briefing_engine import OutputBriefingEngineSnapshotORM, OutputBriefingEngineWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/output_briefing_engine_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    OutputBriefingEngineWorkspaceORM.metadata.create_all(bind=db_session.engine)
    OutputBriefingEngineSnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_output_briefing_engine_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/output-briefing-engine/workspaces',
        json={
            'name': 'Output Workspace',
            'owner': 'blake',
            'description': 'Tracks briefing templates, evidence packs, and output readiness.',
            'briefing_domains': ['executive briefs', 'alerts'],
            'output_goals': ['clarity', 'distribution readiness'],
            'linked_apps': [],
            'linked_brain_modules': ['memory', 'reasoning'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/output-briefing-engine/workspaces/{workspace_id}/snapshot',
        json={
            'briefing_templates': ['executive memo template'],
            'distribution_rules': ['send weekly to leadership'],
            'alert_formats': ['urgent risk alert'],
            'evidence_packs': ['decision evidence pack'],
            'risks': ['unclear briefing'],
            'opportunities': ['improve executive communication'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'output_quality_score': 79,
            'briefing_readiness_score': 74,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['output_quality_score'] == 79

    status = client.post(
        f'/api/v1/output-briefing-engine/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/output-briefing-engine/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/output-briefing-engine/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_output_quality_score'] >= 0
    assert summary_payload['average_briefing_readiness_score'] >= 0
