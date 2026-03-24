from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.software_engineering import CreateEngineeringProjectRequest, UpdateEngineeringProjectStatusRequest, UpsertEngineeringExecutionRequest, UpsertEngineeringExperimentRequest, UpsertEngineeringResearchRequest
from packages.domain.software_engineering import EngineeringExecutionRecord, EngineeringExperimentRecord, EngineeringProject, EngineeringProjectStatus, EngineeringProjectType, EngineeringResearchRecord
from packages.repositories.software_engineering import EngineeringExecutionRepository, EngineeringExperimentRepository, EngineeringProjectRepository, EngineeringResearchRepository
from packages.services.software_engineering_engines import CUTTING_EDGE_TOOL_STACK, evaluate_engineering_execution, evaluate_engineering_experiments, evaluate_engineering_research
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix='/api/v1/software-engineering', tags=['software_engineering'])
telemetry = TelemetryLogger(filepath='var/software_engineering_telemetry.jsonl')

@router.post('/projects')
def create_engineering_project(payload: CreateEngineeringProjectRequest, db: Session = Depends(get_db)) -> dict:
    try:
        project_type = EngineeringProjectType(payload.project_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid project_type') from exc
    repo = EngineeringProjectRepository(db)
    project = EngineeringProject(name=payload.name, project_type=project_type, owner=payload.owner, description=payload.description, languages=payload.languages, frameworks=payload.frameworks, goals=payload.goals, linked_apps=payload.linked_apps, linked_brain_modules=payload.linked_brain_modules)
    saved = repo.create(project)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='create_engineering_project', project_id=saved.id, project_type=saved.project_type.value)
    return saved.model_dump(mode='json')

@router.get('/projects')
def list_engineering_projects(db: Session = Depends(get_db)) -> list[dict]:
    repo = EngineeringProjectRepository(db)
    payload = [item.model_dump(mode='json') for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='list_engineering_projects', returned_count=len(payload))
    return payload

@router.post('/projects/{project_id}/status')
def update_engineering_project_status(project_id: str, payload: UpdateEngineeringProjectStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = EngineeringProjectStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='invalid status') from exc
    repo = EngineeringProjectRepository(db)
    project = repo.update_status(project_id, status)
    if project is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='update_engineering_project_status', project_id=project_id, status=project.status.value)
    return project.model_dump(mode='json')

@router.post('/projects/{project_id}/research')
def upsert_engineering_research(project_id: str, payload: UpsertEngineeringResearchRequest, db: Session = Depends(get_db)) -> dict:
    if EngineeringProjectRepository(db).get(project_id) is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    repo = EngineeringResearchRepository(db)
    record = EngineeringResearchRecord(project_id=project_id, **payload.model_dump())
    saved = repo.upsert(record)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_engineering_research', project_id=project_id, modernization_score=saved.modernization_score)
    return saved.model_dump(mode='json')

@router.get('/projects/{project_id}/research-evaluation')
def get_engineering_research_evaluation(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = EngineeringProjectRepository(db).get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    research = EngineeringResearchRepository(db).get(project_id)
    if research is None:
        raise HTTPException(status_code=404, detail='engineering research not found')
    evaluation = evaluate_engineering_research(project, research)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_engineering_research_evaluation', project_id=project_id, confidence_score=evaluation.confidence_score)
    return evaluation.model_dump(mode='json')

@router.post('/projects/{project_id}/execution')
def upsert_engineering_execution(project_id: str, payload: UpsertEngineeringExecutionRequest, db: Session = Depends(get_db)) -> dict:
    if EngineeringProjectRepository(db).get(project_id) is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    repo = EngineeringExecutionRepository(db)
    record = EngineeringExecutionRecord(project_id=project_id, **payload.model_dump())
    saved = repo.upsert(record)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_engineering_execution', project_id=project_id, reliability_score=saved.reliability_score)
    return saved.model_dump(mode='json')

@router.get('/projects/{project_id}/execution-evaluation')
def get_engineering_execution_evaluation(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = EngineeringProjectRepository(db).get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    execution = EngineeringExecutionRepository(db).get(project_id)
    if execution is None:
        raise HTTPException(status_code=404, detail='engineering execution not found')
    evaluation = evaluate_engineering_execution(project, execution)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_engineering_execution_evaluation', project_id=project_id, confidence_score=evaluation.confidence_score)
    return evaluation.model_dump(mode='json')

@router.post('/projects/{project_id}/experiments')
def upsert_engineering_experiments(project_id: str, payload: UpsertEngineeringExperimentRequest, db: Session = Depends(get_db)) -> dict:
    if EngineeringProjectRepository(db).get(project_id) is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    repo = EngineeringExperimentRepository(db)
    record = EngineeringExperimentRecord(project_id=project_id, **payload.model_dump())
    saved = repo.upsert(record)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route='upsert_engineering_experiments', project_id=project_id, experimentation_score=saved.experimentation_score)
    return saved.model_dump(mode='json')

@router.get('/projects/{project_id}/experiment-evaluation')
def get_engineering_experiment_evaluation(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = EngineeringProjectRepository(db).get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='engineering project not found')
    record = EngineeringExperimentRepository(db).get(project_id)
    if record is None:
        raise HTTPException(status_code=404, detail='engineering experiments not found')
    evaluation = evaluate_engineering_experiments(project, record)
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_engineering_experiment_evaluation', project_id=project_id, confidence_score=evaluation.confidence_score)
    return evaluation.model_dump(mode='json')

@router.get('/tool-stack')
def get_software_engineering_tool_stack() -> dict:
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route='get_software_engineering_tool_stack', returned_count=len(CUTTING_EDGE_TOOL_STACK))
    return CUTTING_EDGE_TOOL_STACK
