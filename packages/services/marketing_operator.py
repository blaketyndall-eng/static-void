from datetime import datetime, timezone

from packages.domain.marketing import ContentAsset, MarketingAnalyticsSnapshot, MarketingProject, MarketingResearchRecord
from packages.domain.marketing_operator import (
    MarketingApprovalDecision,
    MarketingDebatePacket,
    MarketingOperatorRun,
    MarketingRiskReview,
)
from packages.services.marketing_learning import review_marketing_project


def build_marketing_debate(
    project: MarketingProject,
    research: MarketingResearchRecord | None,
    assets: list[ContentAsset],
    analytics: MarketingAnalyticsSnapshot | None,
) -> MarketingDebatePacket:
    bull_case = []
    bear_case = []
    unresolved = []

    if research is not None and research.opportunity_score >= 60:
        bull_case.append("Research indicates the market opportunity is viable.")
    else:
        bear_case.append("Research confidence is not yet strong enough.")

    if assets:
        bull_case.append("Content assets exist and can support execution.")
    else:
        bear_case.append("Execution is blocked by missing content assets.")

    if analytics is not None and analytics.quality_score >= 60:
        bull_case.append("Existing analytics quality suggests message-market fit is improving.")
    elif analytics is not None:
        bear_case.append("Analytics suggest execution quality still needs iteration.")
    else:
        unresolved.append("Need analytics to validate execution quality.")

    if not project.channels:
        unresolved.append("Need clearer channel strategy before scaling.")
    if not project.goals:
        unresolved.append("Need explicit goals for execution and measurement.")

    synthesis = (
        f"Marketing debate for {project.name} balances research confidence, channel readiness, and execution proof. "
        f"Operator decision should determine whether to approve, iterate, or hold."
    )
    return MarketingDebatePacket(
        project_id=project.id,
        bull_case=bull_case,
        bear_case=bear_case,
        unresolved_questions=unresolved,
        synthesis=synthesis,
    )


def build_marketing_risk_review(review_score: float, project: MarketingProject, debate: MarketingDebatePacket) -> MarketingRiskReview:
    risks = []
    if review_score < 60:
        risks.append("overall_review_score_below_threshold")
    if not project.channels:
        risks.append("missing_channels")
    if not project.goals:
        risks.append("missing_goals")
    if debate.unresolved_questions:
        risks.append("open_questions_remain")

    if review_score >= 75 and len(risks) <= 1:
        decision = MarketingApprovalDecision.approve
    elif review_score >= 50:
        decision = MarketingApprovalDecision.iterate
    else:
        decision = MarketingApprovalDecision.hold

    reasoning = (
        f"Review score {review_score:.1f} with {len(risks)} flagged risks leads to {decision.value}."
    )
    return MarketingRiskReview(project_id=project.id, decision=decision, top_risks=risks, reasoning=reasoning)


def build_marketing_action_plan(decision: MarketingApprovalDecision, review_lessons: list[str]) -> list[str]:
    if decision == MarketingApprovalDecision.approve:
        return ["Move into channel execution.", "Monitor analytics weekly.", "Prepare next content iteration."]
    if decision == MarketingApprovalDecision.iterate:
        return review_lessons[:3] or ["Refine research and content before scaling."]
    return ["Pause scaling.", "Resolve major research and execution gaps first."]


def build_marketing_operator_run(
    project: MarketingProject,
    research: MarketingResearchRecord | None,
    assets: list[ContentAsset],
    analytics: MarketingAnalyticsSnapshot | None,
) -> MarketingOperatorRun:
    review = review_marketing_project(project, research, assets, analytics)
    debate = build_marketing_debate(project, research, assets, analytics)
    risk_review = build_marketing_risk_review(review.review_score, project, debate)
    action_plan = build_marketing_action_plan(risk_review.decision, review.lessons)

    run = MarketingOperatorRun(
        project_id=project.id,
        stages=[
            {"stage": "review_complete", "review_score": review.review_score},
            {"stage": "debate_complete", "unresolved_questions": debate.unresolved_questions},
            {"stage": "risk_complete", "decision": risk_review.decision.value},
            {"stage": "action_plan_complete", "steps": action_plan},
        ],
        debate=debate,
        risk_review=risk_review,
        action_plan=action_plan,
    )
    run.completed_at = datetime.now(timezone.utc)
    return run
