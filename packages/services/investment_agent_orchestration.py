from datetime import datetime, timezone

from packages.domain.investment import InvestmentThesis
from packages.domain.investment_agents import (
    AgentInput,
    AgentOpinion,
    AgentStance,
    AllocationDecisionRecord,
    ApprovalDecision,
    DebatePacket,
    OperatorDecisionRun,
    RiskReview,
)


def _make_bull_opinion(agent_name: str, thesis: InvestmentThesis, engine_output: dict, profile: dict) -> AgentOpinion:
    positives = []
    if thesis.entry_zone and thesis.target_zone:
        positives.append("Entry and target zones are defined.")
    if thesis.catalysts:
        positives.append("Catalyst path exists.")
    if engine_output.get("confidence_score", 0) >= 60:
        positives.append("Engine confidence is supportive.")
    if profile:
        positives.append("Specialist profile is attached.")
    return AgentOpinion(
        agent_name=agent_name,
        stance=AgentStance.bullish,
        confidence=min(max((engine_output.get("confidence_score", 50) / 100), 0), 1),
        thesis=f"Bull case for {thesis.ticker} centers on setup quality and structured upside.",
        supporting_points=positives or ["Underlying thesis structure is acceptable."],
        risk_points=[],
        evidence_gaps=[] if thesis.catalysts else ["Need clearer catalyst map."],
    )


def _make_bear_opinion(agent_name: str, thesis: InvestmentThesis, engine_output: dict, profile: dict) -> AgentOpinion:
    risks = []
    if thesis.risk_flags:
        risks.extend([f"Risk flag: {flag}" for flag in thesis.risk_flags])
    if not thesis.invalidation:
        risks.append("Invalidation is not explicit.")
    if engine_output.get("confidence_score", 0) < 60:
        risks.append("Engine confidence is not strong enough for approval.")
    gaps = []
    if not thesis.catalysts:
        gaps.append("Need at least one catalyst or timing trigger.")
    return AgentOpinion(
        agent_name=agent_name,
        stance=AgentStance.bearish,
        confidence=min(max((1 - (engine_output.get("confidence_score", 50) / 100)), 0), 1),
        thesis=f"Bear case for {thesis.ticker} centers on fragility, risk load, or insufficient edge clarity.",
        supporting_points=[],
        risk_points=risks or ["Setup may not justify capital yet."],
        evidence_gaps=gaps,
    )


def build_debate_packet(category: str, thesis: InvestmentThesis, engine_output: dict, profile: dict | None = None) -> DebatePacket:
    profile = profile or {}
    bullish = _make_bull_opinion(f"{category}_bull_agent", thesis, engine_output, profile)
    bearish = _make_bear_opinion(f"{category}_bear_agent", thesis, engine_output, profile)
    unresolved = []
    if not thesis.catalysts:
        unresolved.append("What specific event or timing trigger supports the trade?")
    if not thesis.invalidation:
        unresolved.append("What level or condition clearly invalidates the thesis?")
    if thesis.conviction < 0.6:
        unresolved.append("Why should this move beyond watch status with current conviction?")
    synthesis = f"Debate on {thesis.ticker} shows upside case versus risk load; risk gate should determine final action."
    return DebatePacket(
        thesis_id=thesis.id,
        category=category,
        bullish=bullish,
        bearish=bearish,
        unresolved_questions=unresolved,
        synthesis=synthesis,
    )


def build_allocation_decision(thesis: InvestmentThesis, risk_review: RiskReview, engine_output: dict) -> AllocationDecisionRecord:
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
        f"Recommendation state from engine was {engine_output.get('recommendation_state', 'unknown')}"
    )

    return AllocationDecisionRecord(
        thesis_id=thesis.id,
        decision=risk_review.decision,
        target_action=action,
        size_guidance=size_guidance,
        why=why,
    )


def build_operator_run(category: str, thesis: InvestmentThesis, engine_output: dict, risk_review: RiskReview, profile: dict | None = None) -> OperatorDecisionRun:
    debate_packet = build_debate_packet(category, thesis, engine_output, profile)
    allocation = build_allocation_decision(thesis, risk_review, engine_output)
    run = OperatorDecisionRun(
        thesis_id=thesis.id,
        category=category,
        stages=[
            {"stage": "engine_complete", "confidence_score": engine_output.get("confidence_score")},
            {"stage": "debate_complete", "unresolved_questions": debate_packet.unresolved_questions},
            {"stage": "risk_complete", "decision": risk_review.decision.value},
            {"stage": "allocation_complete", "target_action": allocation.target_action},
        ],
        debate_packet=debate_packet,
        risk_review=risk_review,
        allocation_decision=allocation,
    )
    run.completed_at = datetime.now(timezone.utc)
    return run
