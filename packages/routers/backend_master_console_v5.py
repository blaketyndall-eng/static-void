from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.routers.backend_expansion_rollup import _collect
from packages.repositories.system_events import SystemEventRepository
from packages.services.expansion_control import build_expansion_control_summary
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/master-console', tags=['master_console_v5'])
telemetry = TelemetryLogger(filepath='var/master_console_telemetry.jsonl')

EXPANSION_ARMS = {
    'ai_governance',
    'signals_forecasting',
    'research_lab',
    'agent_studio',
    'decision_memory',
    'vertical_packs',
    'integrations_automation',
    'data_source_intelligence',
}


@router.get('/summary-v5')
def get_master_console_summary_v5(db: Session = Depends(get_db)) -> dict:
    arm_summaries = _collect(db)
    expansion = build_expansion_control_summary(arm_summaries)
    recent_activity = [
        item.model_dump(mode='json')
        for item in SystemEventRepository(db).list()
        if item.source_arm in EXPANSION_ARMS
    ]
    payload = {
        'expansion': expansion.model_dump(mode='json'),
        'expansion_active_arm_count': len([item for item in arm_summaries if item.active_count > 0]),
        'expansion_recent_activity': recent_activity[:20],
        'expansion_top_risks': expansion.top_risks[:10],
        'expansion_top_opportunities': expansion.top_opportunities[:10],
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_master_console_summary_v5', returned_count=payload['expansion']['total_workspace_count'])
    return payload
