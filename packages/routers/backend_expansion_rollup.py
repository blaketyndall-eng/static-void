from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.repositories.ai_governance import AIGovernanceSnapshotRepository, AIGovernanceWorkspaceRepository
from packages.repositories.data_source_intelligence import DataSourceIntelligenceSnapshotRepository, DataSourceIntelligenceWorkspaceRepository
from packages.repositories.decision_memory_store import DecisionMemorySnapshotRepository, DecisionMemoryWorkspaceRepository
from packages.repositories.integrations_automation import IntegrationsAutomationSnapshotRepository, IntegrationsAutomationWorkspaceRepository
from packages.repositories.orchestration_studio import AgentStudioSnapshotRepository, AgentStudioWorkspaceRepository
from packages.repositories.research_lab import ResearchLabSnapshotRepository, ResearchLabWorkspaceRepository
from packages.repositories.signals_forecasting import SignalsForecastingSnapshotRepository, SignalsForecastingWorkspaceRepository
from packages.repositories.verticalization_store import VerticalPacksSnapshotRepository, VerticalPacksWorkspaceRepository
from packages.services.ai_governance import build_ai_governance_summary
from packages.services.data_source_intelligence import build_data_source_intelligence_summary
from packages.services.decision_memory_ops import build_decision_memory_summary
from packages.services.expansion_control import ExpansionArmSummary, build_expansion_control_summary
from packages.services.integrations_automation import build_integrations_automation_summary
from packages.services.research_lab import build_research_lab_summary
from packages.services.signals_forecasting import build_signals_forecasting_summary
from packages.services.studio_ops import build_studio_summary
from packages.services.vertical_pack_ops import build_vertical_pack_summary
from packages.storage.session import get_db

router = APIRouter(prefix='/api/v1/expansion-rollup', tags=['expansion_rollup'])


def _collect(db: Session) -> list[ExpansionArmSummary]:
    out: list[ExpansionArmSummary] = []

    w = AIGovernanceWorkspaceRepository(db).list(); srepo = AIGovernanceSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_ai_governance_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='ai_governance', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_governance_score, top_risks=a.top_risks, top_opportunities=a.top_mitigations))

    w = SignalsForecastingWorkspaceRepository(db).list(); srepo = SignalsForecastingSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_signals_forecasting_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='signals_forecasting', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_signal_quality_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = ResearchLabWorkspaceRepository(db).list(); srepo = ResearchLabSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_research_lab_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='research_lab', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_experiment_quality_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = AgentStudioWorkspaceRepository(db).list(); srepo = AgentStudioSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_studio_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='agent_studio', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_routing_quality_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = DecisionMemoryWorkspaceRepository(db).list(); srepo = DecisionMemorySnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_decision_memory_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='decision_memory', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_memory_quality_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = VerticalPacksWorkspaceRepository(db).list(); srepo = VerticalPacksSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_vertical_pack_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='vertical_packs', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_pack_quality_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = IntegrationsAutomationWorkspaceRepository(db).list(); srepo = IntegrationsAutomationSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_integrations_automation_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='integrations_automation', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_integration_health_score, top_risks=a.top_risks, top_opportunities=a.top_opportunities))

    w = DataSourceIntelligenceWorkspaceRepository(db).list(); srepo = DataSourceIntelligenceSnapshotRepository(db); s = {x.id: srepo.get(x.id) for x in w}; s = {k: v for k, v in s.items() if v is not None}; a = build_data_source_intelligence_summary(w, s)
    out.append(ExpansionArmSummary(arm_name='data_source_intelligence', workspace_count=a.workspace_count, active_count=a.active_count, average_score=a.average_source_quality_score, top_risks=a.top_conflicts, top_opportunities=a.top_opportunities))

    return out


@router.get('/summary')
def get_expansion_rollup_summary(db: Session = Depends(get_db)) -> dict:
    return build_expansion_control_summary(_collect(db)).model_dump(mode='json')
