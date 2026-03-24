from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_thesis_id(prefix: str = "thesis") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AssetClass(str, Enum):
    equity = "equity"
    option = "option"
    crypto = "crypto"
    prediction_market = "prediction_market"


class ThesisStatus(str, Enum):
    watch = "watch"
    active = "active"
    scaling = "scaling"
    invalidated = "invalidated"
    closed = "closed"
    reviewed = "reviewed"


class RecommendationState(str, Enum):
    watch = "watch"
    starter = "starter"
    build = "build"
    hold = "hold"
    trim = "trim"
    exit = "exit"
    no_trade = "no_trade"


class EvidenceCategory(str, Enum):
    fundamental = "fundamental"
    valuation = "valuation"
    technical = "technical"
    catalyst = "catalyst"
    management = "management"
    macro = "macro"
    sentiment = "sentiment"
    liquidity = "liquidity"
    regulatory = "regulatory"
    risk_flag = "risk_flag"


class InvestmentThesis(BaseModel):
    id: str = Field(default_factory=new_thesis_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    asset_class: AssetClass
    instrument_type: str
    ticker: str
    asset_name: str
    thesis_type: str
    timeframe: str
    status: ThesisStatus = ThesisStatus.watch
    conviction: float = Field(default=0.5, ge=0, le=1)
    entry_zone: str = ""
    target_zone: str = ""
    invalidation: str = ""
    catalysts: list[dict[str, Any]] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommendation_state: RecommendationState = RecommendationState.watch
    review_date: str | None = None
    portfolio_role: str = "watch"
    evidence_ids: list[str] = Field(default_factory=list)
    notes: str = ""


class SwingTradeProfile(BaseModel):
    setup_type: str
    relative_strength: float | None = None
    atr: float | None = None
    sector_momentum: float | None = None
    chart_structure: str = ""
    gap_risk: str = ""


class OptionsProfile(BaseModel):
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


class CryptoProfile(BaseModel):
    token: str
    chain_or_ecosystem: str = ""
    narrative: str = ""
    unlock_schedule: list[dict[str, Any]] = Field(default_factory=list)
    funding_basis_snapshot: dict[str, Any] = Field(default_factory=dict)
    exchange_liquidity_score: float | None = None
    regime_bucket: str = ""


class PredictionMarketProfile(BaseModel):
    market_venue: str
    contract_text: str
    settlement_rule_summary: str = ""
    event_date: str | None = None
    implied_probability: float | None = Field(default=None, ge=0, le=1)
    estimated_probability: float | None = Field(default=None, ge=0, le=1)
    edge: float | None = None
    max_stake: float | None = None
    ambiguity_score: float | None = Field(default=None, ge=0, le=1)
