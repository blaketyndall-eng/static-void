from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.storage.session import Base


class InvestmentThesisORM(Base):
    __tablename__ = "investment_theses"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    asset_class: Mapped[str] = mapped_column(String(40), index=True)
    instrument_type: Mapped[str] = mapped_column(String(80), index=True)
    ticker: Mapped[str] = mapped_column(String(40), index=True)
    asset_name: Mapped[str] = mapped_column(String(255), index=True)
    thesis_type: Mapped[str] = mapped_column(String(80), index=True)
    timeframe: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    conviction: Mapped[float] = mapped_column(Float, default=0.5)
    entry_zone: Mapped[str] = mapped_column(Text, default="")
    target_zone: Mapped[str] = mapped_column(Text, default="")
    invalidation: Mapped[str] = mapped_column(Text, default="")
    catalysts: Mapped[list[dict]] = mapped_column(JSON, default=list)
    risk_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendation_state: Mapped[str] = mapped_column(String(40), index=True)
    review_date: Mapped[str | None] = mapped_column(String(80), nullable=True)
    portfolio_role: Mapped[str] = mapped_column(String(80), default="watch")
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")


class SwingTradeProfileORM(Base):
    __tablename__ = "investment_swing_profiles"

    thesis_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    setup_type: Mapped[str] = mapped_column(String(80), index=True)
    relative_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    atr: Mapped[float | None] = mapped_column(Float, nullable=True)
    sector_momentum: Mapped[float | None] = mapped_column(Float, nullable=True)
    chart_structure: Mapped[str] = mapped_column(Text, default="")
    gap_risk: Mapped[str] = mapped_column(Text, default="")


class OptionsProfileORM(Base):
    __tablename__ = "investment_options_profiles"

    thesis_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    underlying_ticker: Mapped[str] = mapped_column(String(40), index=True)
    structure_type: Mapped[str] = mapped_column(String(80), index=True)
    expiry: Mapped[str] = mapped_column(String(80), index=True)
    strikes: Mapped[list[float]] = mapped_column(JSON, default=list)
    debit_credit: Mapped[str] = mapped_column(String(20), default="debit")
    max_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_gain: Mapped[float | None] = mapped_column(Float, nullable=True)
    iv_context: Mapped[str] = mapped_column(Text, default="")
    greeks: Mapped[dict] = mapped_column(JSON, default=dict)
    liquidity_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class CryptoProfileORM(Base):
    __tablename__ = "investment_crypto_profiles"

    thesis_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    token: Mapped[str] = mapped_column(String(80), index=True)
    chain_or_ecosystem: Mapped[str] = mapped_column(String(120), default="")
    narrative: Mapped[str] = mapped_column(Text, default="")
    unlock_schedule: Mapped[list[dict]] = mapped_column(JSON, default=list)
    funding_basis_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    exchange_liquidity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    regime_bucket: Mapped[str] = mapped_column(String(80), default="")


class PredictionMarketProfileORM(Base):
    __tablename__ = "investment_prediction_profiles"

    thesis_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    market_venue: Mapped[str] = mapped_column(String(120), index=True)
    contract_text: Mapped[str] = mapped_column(Text)
    settlement_rule_summary: Mapped[str] = mapped_column(Text, default="")
    event_date: Mapped[str | None] = mapped_column(String(80), nullable=True)
    implied_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    edge: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_stake: Mapped[float | None] = mapped_column(Float, nullable=True)
    ambiguity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
