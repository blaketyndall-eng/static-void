from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.contracts.investment import (
    AttachInvestmentEvidenceRequest,
    CreateCryptoProfileRequest,
    CreateInvestmentThesisRequest,
    CreateOptionsProfileRequest,
    CreatePredictionMarketProfileRequest,
    CreateSwingTradeProfileRequest,
    UpdateInvestmentThesisStatusRequest,
)
from packages.domain.investment import (
    AssetClass,
    CryptoProfile,
    InvestmentThesis,
    OptionsProfile,
    PredictionMarketProfile,
    RecommendationState,
    SwingTradeProfile,
    ThesisStatus,
)
from packages.repositories.investment import (
    CryptoProfileRepository,
    InvestmentThesisRepository,
    OptionsProfileRepository,
    PredictionMarketProfileRepository,
    SwingTradeProfileRepository,
)
from packages.storage.session import get_db
from telemetry_events import API_REQUEST_COMPLETED
from telemetry_helpers import emit_action_event, emit_view_event
from telemetry_logger import TelemetryLogger

router = APIRouter(prefix="/api/v1/investment", tags=["investment"])
telemetry = TelemetryLogger(filepath="var/investment_telemetry.jsonl")


@router.post("/theses")
def create_investment_thesis(payload: CreateInvestmentThesisRequest, db: Session = Depends(get_db)) -> dict:
    try:
        asset_class = AssetClass(payload.asset_class)
        recommendation_state = RecommendationState(payload.recommendation_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid investment thesis payload") from exc

    repo = InvestmentThesisRepository(db)
    thesis = InvestmentThesis(
        asset_class=asset_class,
        instrument_type=payload.instrument_type,
        ticker=payload.ticker,
        asset_name=payload.asset_name,
        thesis_type=payload.thesis_type,
        timeframe=payload.timeframe,
        conviction=payload.conviction,
        entry_zone=payload.entry_zone,
        target_zone=payload.target_zone,
        invalidation=payload.invalidation,
        catalysts=payload.catalysts,
        risk_flags=payload.risk_flags,
        recommendation_state=recommendation_state,
        review_date=payload.review_date,
        portfolio_role=payload.portfolio_role,
        notes=payload.notes,
    )
    saved = repo.create(thesis)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_investment_thesis", thesis_id=saved.id, asset_class=saved.asset_class.value)
    return saved.model_dump(mode="json")


@router.get("/theses")
def list_investment_theses(db: Session = Depends(get_db)) -> list[dict]:
    repo = InvestmentThesisRepository(db)
    payload = [item.model_dump(mode="json") for item in repo.list()]
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="list_investment_theses", returned_count=len(payload))
    return payload


@router.get("/theses/{thesis_id}")
def get_investment_thesis(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    thesis = repo.get(thesis_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_investment_thesis", thesis_id=thesis_id)
    return thesis.model_dump(mode="json")


@router.post("/theses/{thesis_id}/status")
def update_investment_thesis_status(thesis_id: str, payload: UpdateInvestmentThesisStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        status = ThesisStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid thesis status") from exc
    repo = InvestmentThesisRepository(db)
    thesis = repo.update_status(thesis_id, status)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="update_investment_thesis_status", thesis_id=thesis_id, status=thesis.status.value)
    return thesis.model_dump(mode="json")


@router.post("/theses/{thesis_id}/evidence")
def attach_investment_evidence(thesis_id: str, payload: AttachInvestmentEvidenceRequest, db: Session = Depends(get_db)) -> dict:
    repo = InvestmentThesisRepository(db)
    thesis = repo.attach_evidence(thesis_id, payload.evidence_id)
    if thesis is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="attach_investment_evidence", thesis_id=thesis_id, evidence_id=payload.evidence_id)
    return thesis.model_dump(mode="json")


@router.post("/theses/{thesis_id}/swing-profile")
def create_swing_profile(thesis_id: str, payload: CreateSwingTradeProfileRequest, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    if thesis_repo.get(thesis_id) is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    repo = SwingTradeProfileRepository(db)
    profile = SwingTradeProfile(**payload.model_dump())
    saved = repo.create(thesis_id, profile)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_swing_profile", thesis_id=thesis_id)
    return saved.model_dump(mode="json")


@router.get("/theses/{thesis_id}/swing-profile")
def get_swing_profile(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = SwingTradeProfileRepository(db)
    profile = repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="swing profile not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_swing_profile", thesis_id=thesis_id)
    return profile.model_dump(mode="json")


@router.post("/theses/{thesis_id}/options-profile")
def create_options_profile(thesis_id: str, payload: CreateOptionsProfileRequest, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    if thesis_repo.get(thesis_id) is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    repo = OptionsProfileRepository(db)
    profile = OptionsProfile(**payload.model_dump())
    saved = repo.create(thesis_id, profile)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_options_profile", thesis_id=thesis_id)
    return saved.model_dump(mode="json")


@router.get("/theses/{thesis_id}/options-profile")
def get_options_profile(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = OptionsProfileRepository(db)
    profile = repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="options profile not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_options_profile", thesis_id=thesis_id)
    return profile.model_dump(mode="json")


@router.post("/theses/{thesis_id}/crypto-profile")
def create_crypto_profile(thesis_id: str, payload: CreateCryptoProfileRequest, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    if thesis_repo.get(thesis_id) is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    repo = CryptoProfileRepository(db)
    profile = CryptoProfile(**payload.model_dump())
    saved = repo.create(thesis_id, profile)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_crypto_profile", thesis_id=thesis_id)
    return saved.model_dump(mode="json")


@router.get("/theses/{thesis_id}/crypto-profile")
def get_crypto_profile(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = CryptoProfileRepository(db)
    profile = repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="crypto profile not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_crypto_profile", thesis_id=thesis_id)
    return profile.model_dump(mode="json")


@router.post("/theses/{thesis_id}/prediction-profile")
def create_prediction_profile(thesis_id: str, payload: CreatePredictionMarketProfileRequest, db: Session = Depends(get_db)) -> dict:
    thesis_repo = InvestmentThesisRepository(db)
    if thesis_repo.get(thesis_id) is None:
        raise HTTPException(status_code=404, detail="investment thesis not found")
    repo = PredictionMarketProfileRepository(db)
    profile = PredictionMarketProfile(**payload.model_dump())
    saved = repo.create(thesis_id, profile)
    emit_action_event(telemetry, API_REQUEST_COMPLETED, route="create_prediction_profile", thesis_id=thesis_id)
    return saved.model_dump(mode="json")


@router.get("/theses/{thesis_id}/prediction-profile")
def get_prediction_profile(thesis_id: str, db: Session = Depends(get_db)) -> dict:
    repo = PredictionMarketProfileRepository(db)
    profile = repo.get(thesis_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="prediction profile not found")
    emit_view_event(telemetry, API_REQUEST_COMPLETED, route="get_prediction_profile", thesis_id=thesis_id)
    return profile.model_dump(mode="json")
