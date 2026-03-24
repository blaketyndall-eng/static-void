from datetime import datetime, timezone

from packages.domain.investment import InvestmentThesis
from packages.domain.investment_agents import (
    AllocationDecisionRecord,
    ApprovalDecision,
    DebatePacket,
    OperatorDecisionRun,
    RiskReview,
)
from packages.services.investment_category_agents import (
    build_crypto_bear_opinion,
    build_crypto_bull_opinion,
    build_options_bear_opinion,
    build_options_bull_opinion,
    build_prediction_bear_opinion,
    build_prediction_bull_opinion,
    build_swing_bear_opinion,
    build_swing_bull_opinion,
)


def build_debate_packet_v2(category: str, thesis: InvestmentThesis, engine_output: dict) -> DebatePacket:
    if category == "equity":
        bullish = build_swing_bull_opinion(thesis, engine_output)
        bearish = build_swing_bear_opinion(thesis, engine_output)
    elif category == "option":
        bullish = build_options_bull_opinion(thesis, engine_output)
        bearish = build_options_bear_opinion(thesis, engine_output)
    elif category == "crypto":
        bullish = build_crypto_bull_opinion(thesis, engine_output)
        bearish = build_crypto_bear_opinion(thesis, engine_output)
    elif category == "prediction_market":
        bullish = build_prediction_bull_opinion(thesis, engine_output)
        bearish = build_prediction_bear_opinion(thesis, engine_output)
    else:
        raise ValueError(f"Unsupported category: {category}")

    unresolved = []
    if not thesis.catalysts:
        unresolved.append("What specific event or timing trigger supports the thesis?")
    if not thesis.invalidation:
        unresolved.append("What explicitly invalidates the setup?")
    if thesis.conviction < 0.6:
        unresolved.append("Why should this move beyond watch status with current conviction?")

    synthesis = (
        f"Category debate for {thesis.ticker} balances structured upside versus execution and risk constraints. "
        f"Risk gate should decide whether the thesis becomes active capital or remains observational."
    )
    return DebatePacket(
        thesis_id=thesis.id,
        category=category,
        bullish=bullish,
        bearish=bearish,
        unresolved_questions=unresolved,
        synthesis=synthesis,
    )


def build_allocation_decision_v2(thesis: InvestmentThesis, risk_review: RiskReview, engine_output: dict) -> AllocationDecisionRecord:
    if risk_review.decision == ApprovalDecision.approve:
        action = "enter_or_add"
        size_guidance = f"Max {risk_review.max_size_pct:.1f}% position sizing"
    elif risk_review.decision == ApprovalDecision.watch_only:
        action = "watch_only"
        size_guidance = f"Monitor only or keep below {risk_review.max_size_pct:.1f}% starter size"
    else:
        action = "reject"
        size_guidance = "No new position"

    why = (
        f"Engine confidence {engine_output.get('confidence_score', 0)} with risk decision {risk_review.decision.value}. "
        f"Engine recommendation was {engine_output.get('recommendation_state', 'unknown')}"
    )

    return AllocationDecisionRecord(
        thesis_id=thesis.id,
        decision=risk_review.decision,
        target_action=action,
        size_guidance=size_guidance,
        why=why,
    )


def build_operator_run_v2(category: str, thesis: InvestmentThesis, engine_output: dict, risk_review: RiskReview) -> OperatorDecisionRun:
    debate_packet = build_debate_packet_v2(category, thesis, engine_output)
    allocation = build_allocation_decision_v2(thesis, risk_review, engine_output)
    run = OperatorDecisionRun(
        thesis_id=thesis.id,
        category=category,
        stages=[
            {"stage": "engine_complete", "confidence_score": engine_output.get("confidence_score")},
            {"stage": "debate_complete", "unresolved_questions": debate_packet.unresolved_questions},
            {"stage": "risk_complete", "decision": risk_review.decision.value, "top_risks": risk_review.top_risks, "overlap_flags": risk_review.overlap_flags},
            {"stage": "allocation_complete", "target_action": allocation.target_action, "size_guidance": allocation.size_guidance},
        ],
        debate_packet=debate_packet,
        risk_review=risk_review,
        allocation_decision=allocation,
    )
    run.completed_at = datetime.now(timezone.utc)
    return run
