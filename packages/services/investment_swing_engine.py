from pydantic import BaseModel, Field

from packages.domain.investment import InvestmentThesis, RecommendationState, SwingTradeProfile


class SwingTradeEvaluation(BaseModel):
    thesis_id: str
    setup_type: str
    trend_score: float = Field(ge=0, le=100)
    momentum_score: float = Field(ge=0, le=100)
    risk_reward_score: float = Field(ge=0, le=100)
    catalyst_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    recommendation_state: RecommendationState
    summary: str
    rationale: str
    invalidation_note: str = ""


def _score_trend(profile: SwingTradeProfile) -> float:
    score = 50.0
    if profile.relative_strength is not None:
        score += max(min(profile.relative_strength * 40, 35), -10)
    if profile.sector_momentum is not None:
        score += max(min(profile.sector_momentum * 25, 20), -10)
    if "breakout" in profile.setup_type:
        score += 10
    if "trend" in profile.chart_structure.lower() or "flag" in profile.chart_structure.lower():
        score += 8
    return max(0.0, min(score, 100.0))


def _score_momentum(profile: SwingTradeProfile) -> float:
    score = 45.0
    if profile.relative_strength is not None:
        score += profile.relative_strength * 35
    if profile.sector_momentum is not None:
        score += profile.sector_momentum * 20
    return max(0.0, min(score, 100.0))


def _score_risk_reward(thesis: InvestmentThesis) -> float:
    score = 50.0
    if thesis.entry_zone and thesis.target_zone:
        score += 20
    if thesis.invalidation:
        score += 20
    if thesis.risk_flags:
        score -= min(len(thesis.risk_flags) * 7, 20)
    return max(0.0, min(score, 100.0))


def _score_catalyst(thesis: InvestmentThesis) -> float:
    score = 35.0
    score += min(len(thesis.catalysts) * 12, 36)
    if thesis.review_date:
        score += 8
    return max(0.0, min(score, 100.0))


def evaluate_swing_trade(thesis: InvestmentThesis, profile: SwingTradeProfile) -> SwingTradeEvaluation:
    trend_score = _score_trend(profile)
    momentum_score = _score_momentum(profile)
    risk_reward_score = _score_risk_reward(thesis)
    catalyst_score = _score_catalyst(thesis)
    confidence_score = round((trend_score * 0.3) + (momentum_score * 0.25) + (risk_reward_score * 0.3) + (catalyst_score * 0.15), 2)

    if confidence_score >= 75:
        recommendation_state = RecommendationState.build
    elif confidence_score >= 60:
        recommendation_state = RecommendationState.starter
    elif confidence_score >= 45:
        recommendation_state = RecommendationState.watch
    else:
        recommendation_state = RecommendationState.no_trade

    summary = f"{profile.setup_type} setup scored {confidence_score:.1f}/100 with {recommendation_state.value} bias."
    rationale = (
        f"Trend {trend_score:.1f}, momentum {momentum_score:.1f}, risk/reward {risk_reward_score:.1f}, "
        f"catalyst {catalyst_score:.1f}. Thesis on {thesis.ticker} is best framed as a {thesis.timeframe} swing setup."
    )

    return SwingTradeEvaluation(
        thesis_id=thesis.id,
        setup_type=profile.setup_type,
        trend_score=trend_score,
        momentum_score=momentum_score,
        risk_reward_score=risk_reward_score,
        catalyst_score=catalyst_score,
        confidence_score=confidence_score,
        recommendation_state=recommendation_state,
        summary=summary,
        rationale=rationale,
        invalidation_note=thesis.invalidation,
    )
