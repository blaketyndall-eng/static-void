from typing import Any

from pydantic import BaseModel, Field


class CreateInvestmentThesisRequest(BaseModel):
    asset_class: str
    instrument_type: str
    ticker: str
    asset_name: str
    thesis_type: str
    timeframe: str
    conviction: float = Field(default=0.5, ge=0, le=1)
    entry_zone: str = ""
    target_zone: str = ""
    invalidation: str = ""
    catalysts: list[dict[str, Any]] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommendation_state: str = "watch"
    review_date: str | None = None
    portfolio_role: str = "watch"
    notes: str = ""


class UpdateInvestmentThesisStatusRequest(BaseModel):
    status: str


class AttachInvestmentEvidenceRequest(BaseModel):
    evidence_id: str


class CreateSwingTradeProfileRequest(BaseModel):
    setup_type: str
    relative_strength: float | None = None
    atr: float | None = None
    sector_momentum: float | None = None
    chart_structure: str = ""
    gap_risk: str = ""


class CreateOptionsProfileRequest(BaseModel):
    underlying_ticker: str
    structure_type: str
    expiry: str
    strikes: list[float] = Field(default_factory=list)
    debit_credit: str = "debit"
    max_loss: float | None = None
    max_gain: float | None = None
    iv_context: str = ""
    greeks: dict[str, float] = Field(default_factory=dict)
    liquidity_score: float | None = None


class CreateCryptoProfileRequest(BaseModel):
    token: str
    chain_or_ecosystem: str = ""
    narrative: str = ""
    unlock_schedule: list[dict[str, Any]] = Field(default_factory=list)
    funding_basis_snapshot: dict[str, Any] = Field(default_factory=dict)
    exchange_liquidity_score: float | None = None
    regime_bucket: str = ""


class CreatePredictionMarketProfileRequest(BaseModel):
    market_venue: str
    contract_text: str
    settlement_rule_summary: str = ""
    event_date: str | None = None
    implied_probability: float | None = Field(default=None, ge=0, le=1)
    estimated_probability: float | None = Field(default=None, ge=0, le=1)
    edge: float | None = None
    max_stake: float | None = None
    ambiguity_score: float | None = Field(default=None, ge=0, le=1)
