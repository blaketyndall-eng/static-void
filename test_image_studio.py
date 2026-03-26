from pathlib import Path

from fastapi.testclient import TestClient

import db_session
from app_sys_v35 import app
from packages.storage.orm_image_studio import ImageStudioRenderJobORM, ImageStudioSnapshotORM, ImageStudioWorkspaceORM
from packages.storage.orm_system_events import SystemEventRecordORM


def reset_state() -> None:
    db_path = Path('decision_intelligence.db')
    if db_path.exists():
        db_path.unlink()
    for path in [Path('var/image_studio_telemetry.jsonl'), Path('var/system_events_telemetry.jsonl')]:
        if path.exists():
            path.unlink()
    ImageStudioWorkspaceORM.metadata.create_all(bind=db_session.engine)
    ImageStudioSnapshotORM.metadata.create_all(bind=db_session.engine)
    ImageStudioRenderJobORM.metadata.create_all(bind=db_session.engine)
    SystemEventRecordORM.metadata.create_all(bind=db_session.engine)


def test_image_studio_workspace_snapshot_jobs_review_and_summary() -> None:
    reset_state()
    client = TestClient(app)

    workspace = client.post(
        '/api/v1/image-studio/workspaces',
        json={
            'name': 'Image Studio Workspace',
            'owner': 'blake',
            'description': 'Tracks image generation, controlled edits, and creative job flow.',
            'creative_domains': ['marketing creative', 'venture concept art'],
            'output_goals': ['variant generation', 'launch asset exploration'],
            'linked_apps': [],
            'linked_modules': ['marketing', 'venture_builder'],
        },
    )
    assert workspace.status_code == 200
    workspace_id = workspace.json()['id']

    snapshot = client.post(
        f'/api/v1/image-studio/workspaces/{workspace_id}/snapshot',
        json={
            'model_registry': ['sd15', 'lcm-lora', 'controlnet-canny', 'inpaint-v1'],
            'generation_modes': ['generate', 'generate_fast', 'generate_controlled', 'inpaint'],
            'prompt_recipes': ['launch concept recipe'],
            'control_profiles': ['canny profile'],
            'edit_profiles': ['mask cleanup profile'],
            'artifact_paths': ['artifacts/image/001.png'],
            'variant_scoring_rules': ['prompt adherence', 'brand fit'],
            'opportunities': ['improve creative speed'],
            'notes': [{'source': 'internal', 'note': 'seed'}],
            'creative_reliability_score': 80,
            'deployment_readiness_score': 74,
        },
    )
    assert snapshot.status_code == 200
    assert snapshot.json()['creative_reliability_score'] == 80

    job = client.post(
        f'/api/v1/image-studio/workspaces/{workspace_id}/jobs',
        json={
            'mode': 'generate_fast',
            'prompt': 'A surreal launch poster for a retro future software company',
            'negative_prompt': 'blurry, low detail',
            'model_name': 'sd15+lcm',
            'width': 768,
            'height': 768,
            'steps': 8,
            'guidance_scale': 2.5,
            'seed': 42,
            'control_type': '',
            'source_asset_path': '',
            'mask_asset_path': '',
            'metadata': {'campaign': 'venture_launch'}
        },
    )
    assert job.status_code == 200
    assert job.json()['mode'] == 'generate_fast'

    status = client.post(
        f'/api/v1/image-studio/workspaces/{workspace_id}/status',
        json={'status': 'active'},
    )
    assert status.status_code == 200
    assert status.json()['status'] == 'active'

    jobs = client.get(f'/api/v1/image-studio/workspaces/{workspace_id}/jobs')
    assert jobs.status_code == 200
    assert len(jobs.json()) >= 1

    job_summary = client.get(f'/api/v1/image-studio/workspaces/{workspace_id}/jobs/summary')
    assert job_summary.status_code == 200
    assert job_summary.json()['queued_jobs'] >= 1

    review = client.get(f'/api/v1/image-studio/workspaces/{workspace_id}/review')
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload['review_score'] >= 0
    assert len(review_payload['top_actions']) >= 1

    summary = client.get('/api/v1/image-studio/summary')
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload['workspace_count'] >= 1
    assert summary_payload['active_count'] >= 1
    assert summary_payload['average_creative_reliability_score'] >= 0
    assert summary_payload['average_deployment_readiness_score'] >= 0
