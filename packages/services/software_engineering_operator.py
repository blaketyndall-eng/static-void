from datetime import datetime, timezone

from packages.domain.software_engineering import (
    EngineeringExecutionRecord,
    EngineeringExperimentRecord,
    EngineeringProject,
    EngineeringResearchRecord,
)
from packages.domain.software_engineering_operator import (
    EngineeringApprovalDecision,
    EngineeringDebatePacket,
    EngineeringOperatorRun,
    EngineeringRiskReview,
)
from packages.services.software_engineering_learning import review_engineering_project


def build_engineering_debate(
    project: EngineeringProject,
    research: EngineeringResearchRecord | None,
    execution: EngineeringExecutionRecord | None,
    experiments: EngineeringExperimentRecord | None,
) -> EngineeringDebatePacket:
    bull_case = []
    bear_case = []
    unresolved = []

    if research is not None and research.modernization_score >= 60:
        bull_case.append("Research indicates the stack and architecture direction are modernizing well.")
    else:
        bear_case.append("Architecture and modernization confidence are still weak.")

    if execution is not None and execution.reliability_score >= 65:
        bull_case.append("Execution reliability suggests the system can support continued iteration.")
    elif execution is not None:
        bear_case.append("Execution quality suggests reliability or delivery needs work.")
    else:
        unresolved.append("Need execution tracking to validate current delivery health.")

    if experiments is not None and experiments.adoption_candidates:
        bull_case.append("Experiments are producing potential adoption candidates.")
    elif experiments is not None:
        bear_case.append("Experiments exist but are not yet translating into adoption candidates.")
    else:
        unresolved.append("Need experimentation evidence for cutting-edge adoption decisions.")

    if not project.frameworks:
        unresolved.append("Need clearer framework and platform inventory.")
    if not project.goals:
        unresolved.append("Need explicit engineering goals and success criteria.")

    synthesis = (
        f"Engineering debate for {project.name} balances modernization, delivery health, and experimentation readiness. "
        f"Operator decision should determine whether to approve, iterate, or hold."
    )
    return EngineeringDebatePacket(
        project_id=project.id,
        bull_case=bull_case,
        bear_case=bear_case,
        unresolved_questions=unresolved,
        synthesis=synthesis,
    )


def build_engineering_risk_review(review_score: float, project: EngineeringProject, debate: EngineeringDebatePacket) -> EngineeringRiskReview:
    risks = []
    if review_score < 60:
        risks.append("overall_review_score_below_threshold")
    if not project.frameworks:
        risks.append("missing_framework_inventory")
    if not project.goals:
        risks.append("missing_goals")
    if debate.unresolved_questions:
        risks.append("open_questions_remain")

    if review_score >= 75 and len(risks) <= 1:
        decision = EngineeringApprovalDecision.approve
    elif review_score >= 50:
        decision = EngineeringApprovalDecision.iterate
    else:
        decision = EngineeringApprovalDecision.hold

    reasoning = f"Review score {review_score:.1f} with {len(risks)} flagged risks leads to {decision.value}."
    return EngineeringRiskReview(project_id=project.id, decision=decision, top_risks=risks, reasoning=reasoning)


def build_engineering_action_plan(decision: EngineeringApprovalDecision, review_lessons: list[str]) -> list[str]:
    if decision == EngineeringApprovalDecision.approve:
        return ["Move into prioritized execution.", "Track reliability and delivery weekly.", "Promote the best experiment candidates into adoption review."]
    if decision == EngineeringApprovalDecision.iterate:
        return review_lessons[:3] or ["Refine research, execution, and experimentation before scaling."]
    return ["Pause major rollout.", "Resolve architecture and delivery risks first."]


def build_engineering_operator_run(
    project: EngineeringProject,
    research: EngineeringResearchRecord | None,
    execution: EngineeringExecutionRecord | None,
    experiments: EngineeringExperimentRecord | None,
) -> EngineeringOperatorRun:
    review = review_engineering_project(project, research, execution, experiments)
    debate = build_engineering_debate(project, research, execution, experiments)
    risk_review = build_engineering_risk_review(review.review_score, project, debate)
    action_plan = build_engineering_action_plan(risk_review.decision, review.lessons)

    run = EngineeringOperatorRun(
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
