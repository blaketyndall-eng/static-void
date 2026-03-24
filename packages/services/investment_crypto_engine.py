from pydantic import BaseModel, Field

from packages.domain.investment import CryptoProfile, InvestmentThesis, RecommendationState


class CryptoStrategyEvaluation(BaseModel):
    thesis_id: str
    token: str
    regime_score: float = Field(ge=0, le=100)
    narrative_score: float = Field(ge=0, le=100)
    liquidity_score: float = Field(ge=0, le=100)
    catalyst_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    recommendation_state: RecommendationState
    summary: str
    rationale: str
    regime_note: str = ""


def _score_regime(profile: CryptoProfile, thesis: InvestmentThesis) -> float:
    score = 45.0
    bucket = profile.regime_bucket.lower()
    if bucket in {"risk_on", "trend", "bullish"}:
        score += 20
    elif bucket in {"risk_off", "bearish"}:
        score -= 10
    if thesis.conviction is not None:
        score += thesis.conviction * 20
    return max(0.0, min(score, 100.0))


def _score_narrative(profile: CryptoProfile) -> float:
    score = 40.0
    if profile.narrative:
        score += 20
    if profile.chain_or_ecosystem:
        score += 10
    if profile.unlock_schedule:
        score -= min(len(profile.unlock_schedule) * 5, 15)
    return max(0.0, min(score, 100.0))


def _score_liquidity(profile: CryptoProfile) -> float:
    score = 35.0
    if profile.exchange_liquidity_score is not None:
        score += profile.exchange_liquidity_score * 55
    return max(0.0, min(score, 100.0))


def _score_catalyst(thesis: InvestmentThesis) -> float:
    score = 35.0
    score += min(len(thesis.catalysts) * 10, 30)
    if thesis.entry_zone and thesis.target_zone:
        score += 10
    if thesis.risk_flags:
        score -= min(len(thesis.risk_flags) * 5, 15)
    return max(0.0, min(score, 100.0))


def evaluate_crypto_strategy(thesis: InvestmentThesis, profile: CryptoProfile) -> CryptoStrategyEvaluation:
    regime_score = _score_regime(profile, thesis)
    narrative_score = _score_narrative(profile)
    liquidity_score = _score_liquidity(profile)
    catalyst_score = _score_catalyst(thesis)
    confidence_score = round(
        (regime_score * 0.3)
        + (narrative_score * 0.25)
        + (liquidity_score * 0.25)
        + (catalyst_score * 0.2),
        2,
    )

    if confidence_score >= 75:
        recommendation_state = RecommendationState.build
    elif confidence_score >= 60:
        recommendation_state = RecommendationState.starter
    elif confidence_score >= 45:
        recommendation_state = RecommendationState.watch
    else:
        recommendation_state = RecommendationState.no_trade

    summary = f"Crypto thesis on {profile.token} scored {confidence_score:.1f}/100 with {recommendation_state.value} bias."
    rationale = (
        f"Regime {regime_score:.1f}, narrative {narrative_score:.1f}, liquidity {liquidity_score:.1f}, "
        f"catalyst {catalyst_score:.1f}. Thesis on {thesis.ticker} is framed as a {thesis.timeframe} crypto setup."
    )

    return CryptoStrategyEvaluation(
        thesis_id=thesis.id,
        token=profile.token,
        regime_score=regime_score,
        narrative_score=narrative_score,
        liquidity_score=liquidity_score,
        catalyst_score=catalyst_score,
        confidence_score=confidence_score,
        recommendation_state=recommendation_state,
        summary=summary,
        rationale=rationale,
        regime_note=profile.regime_bucket,
    )
