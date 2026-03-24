from packages.domain.investment import InvestmentThesis
from packages.domain.investment_agents import ApprovalDecision, RiskReview


def build_risk_review(
    thesis: InvestmentThesis,
    engine_confidence_score: float,
    *,
    liquidity_score: float | None = None,
    ambiguity_score: float | None = None,
    overlap_flags: list[str] | None = None,
) -> RiskReview:
    overlap_flags = overlap_flags or []
    top_risks = list(thesis.risk_flags)
    liquidity_warnings: list[str] = []

    decision = ApprovalDecision.watch_only
    max_size_pct = 2.0

    if liquidity_score is not None and liquidity_score < 50:
        liquidity_warnings.append("Liquidity score is weak for preferred sizing.")
        top_risks.append("low_liquidity")

    if ambiguity_score is not None and ambiguity_score > 0.25:
        top_risks.append("high_ambiguity")

    if overlap_flags:
        top_risks.extend([f"overlap:{flag}" for flag in overlap_flags])

    risk_penalty = min(len(top_risks) * 6, 30)
    adjusted_confidence = max(engine_confidence_score - risk_penalty, 0)

    if adjusted_confidence >= 75 and not liquidity_warnings and "high_ambiguity" not in top_risks:
        decision = ApprovalDecision.approve
        max_size_pct = 5.0
    elif adjusted_confidence >= 55:
        decision = ApprovalDecision.watch_only
        max_size_pct = 2.5
    else:
        decision = ApprovalDecision.reject
        max_size_pct = 0.0

    reasoning = (
        f"Engine confidence {engine_confidence_score:.1f} adjusted by risk penalty {risk_penalty}. "
        f"Decision is {decision.value} with max size {max_size_pct:.1f}% of book."
    )

    return RiskReview(
        thesis_id=thesis.id,
        decision=decision,
        max_size_pct=max_size_pct,
        top_risks=top_risks,
        overlap_flags=overlap_flags,
        liquidity_warnings=liquidity_warnings,
        reasoning=reasoning,
    )
