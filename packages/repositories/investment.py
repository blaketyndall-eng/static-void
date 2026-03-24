from sqlalchemy.orm import Session

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
from packages.storage.orm_investment import (
    CryptoProfileORM,
    InvestmentThesisORM,
    OptionsProfileORM,
    PredictionMarketProfileORM,
    SwingTradeProfileORM,
)


class InvestmentThesisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[InvestmentThesis]:
        rows = self.db.query(InvestmentThesisORM).order_by(InvestmentThesisORM.ticker.asc()).all()
        return [self._to_domain(row) for row in rows]

    def create(self, thesis: InvestmentThesis) -> InvestmentThesis:
        row = InvestmentThesisORM(
            id=thesis.id,
            asset_class=thesis.asset_class.value,
            instrument_type=thesis.instrument_type,
            ticker=thesis.ticker,
            asset_name=thesis.asset_name,
            thesis_type=thesis.thesis_type,
            timeframe=thesis.timeframe,
            status=thesis.status.value,
            conviction=thesis.conviction,
            entry_zone=thesis.entry_zone,
            target_zone=thesis.target_zone,
            invalidation=thesis.invalidation,
            catalysts=thesis.catalysts,
            risk_flags=thesis.risk_flags,
            recommendation_state=thesis.recommendation_state.value,
            review_date=thesis.review_date,
            portfolio_role=thesis.portfolio_role,
            evidence_ids=thesis.evidence_ids,
            notes=thesis.notes,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, thesis_id: str) -> InvestmentThesis | None:
        row = self.db.get(InvestmentThesisORM, thesis_id)
        if row is None:
            return None
        return self._to_domain(row)

    def update_status(self, thesis_id: str, status: ThesisStatus) -> InvestmentThesis | None:
        row = self.db.get(InvestmentThesisORM, thesis_id)
        if row is None:
            return None
        row.status = status.value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def attach_evidence(self, thesis_id: str, evidence_id: str) -> InvestmentThesis | None:
        row = self.db.get(InvestmentThesisORM, thesis_id)
        if row is None:
            return None
        current = row.evidence_ids or []
        row.evidence_ids = [*current, evidence_id]
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: InvestmentThesisORM) -> InvestmentThesis:
        return InvestmentThesis(
            id=row.id,
            asset_class=AssetClass(row.asset_class),
            instrument_type=row.instrument_type,
            ticker=row.ticker,
            asset_name=row.asset_name,
            thesis_type=row.thesis_type,
            timeframe=row.timeframe,
            status=ThesisStatus(row.status),
            conviction=row.conviction,
            entry_zone=row.entry_zone,
            target_zone=row.target_zone,
            invalidation=row.invalidation,
            catalysts=row.catalysts or [],
            risk_flags=row.risk_flags or [],
            recommendation_state=RecommendationState(row.recommendation_state),
            review_date=row.review_date,
            portfolio_role=row.portfolio_role,
            evidence_ids=row.evidence_ids or [],
            notes=row.notes,
        )


class SwingTradeProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, thesis_id: str, profile: SwingTradeProfile) -> SwingTradeProfile:
        row = SwingTradeProfileORM(
            thesis_id=thesis_id,
            setup_type=profile.setup_type,
            relative_strength=profile.relative_strength,
            atr=profile.atr,
            sector_momentum=profile.sector_momentum,
            chart_structure=profile.chart_structure,
            gap_risk=profile.gap_risk,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, thesis_id: str) -> SwingTradeProfile | None:
        row = self.db.get(SwingTradeProfileORM, thesis_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: SwingTradeProfileORM) -> SwingTradeProfile:
        return SwingTradeProfile(
            setup_type=row.setup_type,
            relative_strength=row.relative_strength,
            atr=row.atr,
            sector_momentum=row.sector_momentum,
            chart_structure=row.chart_structure,
            gap_risk=row.gap_risk,
        )


class OptionsProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, thesis_id: str, profile: OptionsProfile) -> OptionsProfile:
        row = OptionsProfileORM(
            thesis_id=thesis_id,
            underlying_ticker=profile.underlying_ticker,
            structure_type=profile.structure_type,
            expiry=profile.expiry,
            strikes=profile.strikes,
            debit_credit=profile.debit_credit,
            max_loss=profile.max_loss,
            max_gain=profile.max_gain,
            iv_context=profile.iv_context,
            greeks=profile.greeks,
            liquidity_score=profile.liquidity_score,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, thesis_id: str) -> OptionsProfile | None:
        row = self.db.get(OptionsProfileORM, thesis_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: OptionsProfileORM) -> OptionsProfile:
        return OptionsProfile(
            underlying_ticker=row.underlying_ticker,
            structure_type=row.structure_type,
            expiry=row.expiry,
            strikes=row.strikes or [],
            debit_credit=row.debit_credit,
            max_loss=row.max_loss,
            max_gain=row.max_gain,
            iv_context=row.iv_context,
            greeks=row.greeks or {},
            liquidity_score=row.liquidity_score,
        )


class CryptoProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, thesis_id: str, profile: CryptoProfile) -> CryptoProfile:
        row = CryptoProfileORM(
            thesis_id=thesis_id,
            token=profile.token,
            chain_or_ecosystem=profile.chain_or_ecosystem,
            narrative=profile.narrative,
            unlock_schedule=profile.unlock_schedule,
            funding_basis_snapshot=profile.funding_basis_snapshot,
            exchange_liquidity_score=profile.exchange_liquidity_score,
            regime_bucket=profile.regime_bucket,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, thesis_id: str) -> CryptoProfile | None:
        row = self.db.get(CryptoProfileORM, thesis_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: CryptoProfileORM) -> CryptoProfile:
        return CryptoProfile(
            token=row.token,
            chain_or_ecosystem=row.chain_or_ecosystem,
            narrative=row.narrative,
            unlock_schedule=row.unlock_schedule or [],
            funding_basis_snapshot=row.funding_basis_snapshot or {},
            exchange_liquidity_score=row.exchange_liquidity_score,
            regime_bucket=row.regime_bucket,
        )


class PredictionMarketProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, thesis_id: str, profile: PredictionMarketProfile) -> PredictionMarketProfile:
        row = PredictionMarketProfileORM(
            thesis_id=thesis_id,
            market_venue=profile.market_venue,
            contract_text=profile.contract_text,
            settlement_rule_summary=profile.settlement_rule_summary,
            event_date=profile.event_date,
            implied_probability=profile.implied_probability,
            estimated_probability=profile.estimated_probability,
            edge=profile.edge,
            max_stake=profile.max_stake,
            ambiguity_score=profile.ambiguity_score,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_domain(row)

    def get(self, thesis_id: str) -> PredictionMarketProfile | None:
        row = self.db.get(PredictionMarketProfileORM, thesis_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: PredictionMarketProfileORM) -> PredictionMarketProfile:
        return PredictionMarketProfile(
            market_venue=row.market_venue,
            contract_text=row.contract_text,
            settlement_rule_summary=row.settlement_rule_summary,
            event_date=row.event_date,
            implied_probability=row.implied_probability,
            estimated_probability=row.estimated_probability,
            edge=row.edge,
            max_stake=row.max_stake,
            ambiguity_score=row.ambiguity_score,
        )
