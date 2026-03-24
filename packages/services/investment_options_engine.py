from pydantic import BaseModel, Field

from packages.domain.investment import InvestmentThesis, OptionsProfile, RecommendationState


class OptionsStrategyEvaluation(BaseModel):
    thesis_id: str
    structure_type: str
    direction_score: float = Field(ge=0, le=100)
    volatility_score: float = Field(ge=0, le=100)
    payoff_score: float = Field(ge=0, le=100)
    liquidity_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    recommendation_state: RecommendationState
    summary: str
    rationale: str
    max_loss_note: str = ""


def _score_direction(thesis: InvestmentThesis) -> float:
    score = 45.0
    if thesis.conviction is not None:
        score += thesis.conviction * 35
    if thesis.entry_zone and thesis.target_zone:
        score += 10
    if thesis.invalidation:
        score += 10
    return max(0.0, min(score, 100.0))


def _score_volatility(profile: OptionsProfile) -> float:
    score = 50.0
    text = profile.iv_context.lower()
    if "acceptable" in text or "favorable" in text or "cheap" in text:
        score += 20
    if "elevated" in text:
        score += 5
    if "expensive" in text or "stretched" in text:
        score -= 15
    if profile.debit_credit == "debit":
        score += 5
    return max(0.0, min(score, 100.0))


def _score_payoff(profile: OptionsProfile) -> float:
    score = 45.0
    if profile.max_loss is not None:
        score += 15
    if profile.max_gain is not None and profile.max_loss is not None and profile.max_loss > 0:
        ratio = profile.max_gain / profile.max_loss
        score += min(ratio * 10, 25)
    if profile.structure_type in {"call_vertical", "put_vertical", "call_debit_spread", "put_debit_spread"}:
        score += 10
    return max(0.0, min(score, 100.0))


def _score_liquidity(profile: OptionsProfile) -> float:
    score = 40.0
    if profile.liquidity_score is not None:
        score += profile.liquidity_score * 50
    if len(profile.strikes) >= 2:
        score += 10
    return max(0.0, min(score, 100.0))


def evaluate_options_strategy(thesis: InvestmentThesis, profile: OptionsProfile) -> OptionsStrategyEvaluation:
    direction_score = _score_direction(thesis)
    volatility_score = _score_volatility(profile)
    payoff_score = _score_payoff(profile)
    liquidity_score = _score_liquidity(profile)
    confidence_score = round(
        (direction_score * 0.3)
        + (volatility_score * 0.2)
        + (payoff_score * 0.3)
        + (liquidity_score * 0.2),
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

    summary = f"{profile.structure_type} scored {confidence_score:.1f}/100 with {recommendation_state.value} bias."
    rationale = (
        f"Direction {direction_score:.1f}, volatility {volatility_score:.1f}, payoff {payoff_score:.1f}, "
        f"liquidity {liquidity_score:.1f}. Thesis on {thesis.ticker} is best framed as an options structure in the {thesis.timeframe} window."
    )
    max_loss_note = f"Max loss set at {profile.max_loss}" if profile.max_loss is not None else ""

    return OptionsStrategyEvaluation(
        thesis_id=thesis.id,
        structure_type=profile.structure_type,
        direction_score=direction_score,
        volatility_score=volatility_score,
        payoff_score=payoff_score,
        liquidity_score=liquidity_score,
        confidence_score=confidence_score,
        recommendation_state=recommendation_state,
        summary=summary,
        rationale=rationale,
        max_loss_note=max_loss_note,
    )
