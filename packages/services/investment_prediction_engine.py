from pydantic import BaseModel, Field

from packages.domain.investment import InvestmentThesis, PredictionMarketProfile, RecommendationState


class PredictionMarketEvaluation(BaseModel):
    thesis_id: str
    market_venue: str
    edge_score: float = Field(ge=0, le=100)
    calibration_score: float = Field(ge=0, le=100)
    clarity_score: float = Field(ge=0, le=100)
    sizing_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    recommendation_state: RecommendationState
    summary: str
    rationale: str
    edge_note: str = ""


def _score_edge(profile: PredictionMarketProfile) -> float:
    score = 35.0
    if profile.edge is not None:
        score += min(max(profile.edge * 200, -20), 40)
    if profile.implied_probability is not None and profile.estimated_probability is not None:
        diff = abs(profile.estimated_probability - profile.implied_probability)
        score += min(diff * 100, 25)
    return max(0.0, min(score, 100.0))


def _score_calibration(profile: PredictionMarketProfile) -> float:
    score = 45.0
    if profile.estimated_probability is not None and profile.implied_probability is not None:
        diff = abs(profile.estimated_probability - profile.implied_probability)
        score += max(20 - (diff * 50), 0)
    if profile.edge is not None and profile.edge > 0:
        score += 10
    return max(0.0, min(score, 100.0))


def _score_clarity(profile: PredictionMarketProfile) -> float:
    score = 50.0
    if profile.settlement_rule_summary:
        score += 20
    if profile.contract_text:
        score += 10
    if profile.ambiguity_score is not None:
        score += max(20 - (profile.ambiguity_score * 40), -20)
    return max(0.0, min(score, 100.0))


def _score_sizing(profile: PredictionMarketProfile) -> float:
    score = 45.0
    if profile.max_stake is not None:
        score += 15
    if profile.edge is not None and profile.edge > 0:
        score += 10
    if profile.ambiguity_score is not None and profile.ambiguity_score < 0.2:
        score += 10
    return max(0.0, min(score, 100.0))


def evaluate_prediction_market(thesis: InvestmentThesis, profile: PredictionMarketProfile) -> PredictionMarketEvaluation:
    edge_score = _score_edge(profile)
    calibration_score = _score_calibration(profile)
    clarity_score = _score_clarity(profile)
    sizing_score = _score_sizing(profile)
    confidence_score = round(
        (edge_score * 0.35)
        + (calibration_score * 0.2)
        + (clarity_score * 0.25)
        + (sizing_score * 0.2),
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

    summary = f"Prediction contract on {profile.market_venue} scored {confidence_score:.1f}/100 with {recommendation_state.value} bias."
    rationale = (
        f"Edge {edge_score:.1f}, calibration {calibration_score:.1f}, clarity {clarity_score:.1f}, sizing {sizing_score:.1f}. "
        f"Thesis on {thesis.ticker} is framed as a {thesis.timeframe} event-probability setup."
    )
    edge_note = f"Estimated edge: {profile.edge}" if profile.edge is not None else ""

    return PredictionMarketEvaluation(
        thesis_id=thesis.id,
        market_venue=profile.market_venue,
        edge_score=edge_score,
        calibration_score=calibration_score,
        clarity_score=clarity_score,
        sizing_score=sizing_score,
        confidence_score=confidence_score,
        recommendation_state=recommendation_state,
        summary=summary,
        rationale=rationale,
        edge_note=edge_note,
    )
