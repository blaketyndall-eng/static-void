from pydantic import BaseModel, Field

from packages.domain.opportunity_hunter import OpportunityCandidate, OpportunityLearningSnapshot, OpportunityMarketSignal, OpportunityScan


class OpportunityEvaluation(BaseModel):
    candidate_id: str
    demand_score: float = Field(ge=0, le=100)
    competition_score: float = Field(ge=0, le=100)
    whitespace_score: float = Field(ge=0, le=100)
    execution_fit_score: float = Field(ge=0, le=100)
    priority_score: float = Field(ge=0, le=100)
    summary: str
    next_actions: list[str] = Field(default_factory=list)


OPPORTUNITY_SOURCE_STACK = {
    "trend_research": ["Google Trends", "Exploding Topics"],
    "scraping_and_research": ["Apify", "Playwright", "Unstructured"],
    "industry_and_labor": ["BLS API", "U.S. Census API", "FRED API"],
    "research_and_technology": ["OpenAlex API"],
    "workflow_and_analytics": ["Temporal", "LangGraph", "PostHog"],
}


def evaluate_opportunity_candidate(candidate: OpportunityCandidate, signal: OpportunityMarketSignal | None = None) -> OpportunityEvaluation:
    signal = signal or OpportunityMarketSignal(candidate_id=candidate.id)
    demand_score = min(candidate.demand_score + (10 if signal.trend_signal else 0) + (8 if signal.research_signal else 0), 100)
    competition_score = candidate.competition_score
    whitespace_score = min(candidate.whitespace_score + (8 if signal.industry_signal else 0) + (8 if signal.labor_signal else 0), 100)
    execution_fit_score = 45.0
    if candidate.related_apps:
        execution_fit_score += 20
    if candidate.related_industries:
        execution_fit_score += 15
    if candidate.target_users:
        execution_fit_score += 10
    execution_fit_score = min(execution_fit_score, 100)

    priority_score = round((demand_score * 0.3) + ((100 - competition_score) * 0.2) + (whitespace_score * 0.3) + (execution_fit_score * 0.2), 2)
    next_actions = []
    if demand_score < 60:
        next_actions.append("Validate demand with trend and search data.")
    if whitespace_score < 60:
        next_actions.append("Look for narrower underserved segments or workflow gaps.")
    if execution_fit_score < 60:
        next_actions.append("Map opportunity to active apps, operators, or builder templates.")
    if not next_actions:
        next_actions.append("Advance to validation sprint and market sizing.")

    return OpportunityEvaluation(
        candidate_id=candidate.id,
        demand_score=demand_score,
        competition_score=competition_score,
        whitespace_score=whitespace_score,
        execution_fit_score=execution_fit_score,
        priority_score=priority_score,
        summary=f"Opportunity candidate {candidate.title} scored {priority_score:.1f}/100 on priority.",
        next_actions=next_actions,
    )


def summarize_scan(scan: OpportunityScan, candidates: list[OpportunityCandidate], learning: OpportunityLearningSnapshot) -> dict:
    return {
        "scan": scan.model_dump(mode="json"),
        "candidate_count": len(candidates),
        "top_candidates": [item.model_dump(mode="json") for item in sorted(candidates, key=lambda x: x.priority_score, reverse=True)[:10]],
        "learning": learning.model_dump(mode="json"),
        "source_stack": OPPORTUNITY_SOURCE_STACK,
    }
