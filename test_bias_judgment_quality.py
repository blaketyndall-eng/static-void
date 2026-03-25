from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v29 import app
from packages.storage.orm_bias_judgment_quality import BiasJudgmentQualitySnapshotORM, BiasJudgmentQualityWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/bias_judgment_quality_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    BiasJudgmentQualityWorkspaceORM.metadata.create_all(bind=db_session.engine)
    BiasJudgmentQualitySnapshotORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_bias_judgment_quality_workspace_snapshot_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/bias-judgment-quality/workspaces',
        json={
            'name': 'Bias Workspace',
            'owner': 'blake',
            'description': 'Tracks bias checks, dissent prompts, and calibration readiness.',
            'judgment_domains': ['vendor evaluation', 'strategy calls'],
            'quality_goals': ['calibration', 'bias reduction'],
            'linked_apps': [],
            'linked_brain_modules': ['reasoning', 'memory'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/bias-judgment-quality/workspaces/{workspace_id}/snapshot',
        json={
            'bias_checks': ['anchoring check'],
            'calibration_rules': ['lower confidence on weak evidence'],
            'dissent_prompts': ['what if the opposite is true?'],
            'assumption_audits': ['assumption audit v1'],
            'risks': ['groupthink risk'],
            'opportunities': ['improve decision discipline'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'judgment_quality_score': 77,
            'calibration_readiness_score': 71,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['judgment_quality_score'] == 77

    status = client.post(
        f'/api/v1/bias-judgment-quality/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    review = client.get(f'/api/v1/bias-judgment-quality/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/bias-judgment-quality/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_judgment_quality_score'] >= 0
    assert summary_payload['average_calibration_readiness_score'] >= 0
