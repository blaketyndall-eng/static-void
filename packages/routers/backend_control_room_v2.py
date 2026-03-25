from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.system_events import SystemEventRepository
from packages.services.expansion_control import build_expansion_control_summary
from packages.services.system_event_helpers import SYSTEM_EVENT_SOURCE_ARMS
from packages.storage.session import get_db
from packages.routers.backend_expansion_rollup import _collect
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/control-room', tags=['control_room_v2'])
telemetry = TelemetryLogger(filepath='var/control_room_telemetry.jsonl')

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


@router.get('/summary-v2')
def get_control_room_summary_v2(db: Session = Depends(get_db)) -> dict:
    arm_summaries = _collect(db)
    expansion = build_expansion_control_summary(arm_summaries)
    recent_activity = [
        item.model_dump(mode='json')
        for item in SystemEventRepository(db).list()
        if item.source_arm in EXPANSION_ARMS
    ]
    payload = {
        'expansion_rollup': expansion.model_dump(mode='json'),
        'recent_activity': recent_activity[:25],
        'top_risks': expansion.top_risks[:10],
        'top_opportunities': expansion.top_opportunities[:10],
        'active_arm_count': len([item for item in arm_summaries if item.active_count > 0]),
        'tracked_arm_count': len(arm_summaries),
    }
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_control_room_summary_v2', returned_count=payload['tracked_arm_count'])
    return payload
