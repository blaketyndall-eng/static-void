from pydantic import BaseModel, Field

from packages.domain.marketing import ContentAsset, MarketingProject, MarketingResearchRecord


class MarketingResearchEvaluation(BaseModel):
    project_id: str
    market_score: float = Field(ge=0, le=100)
    competitor_score: float = Field(ge=0, le=100)
    audience_score: float = Field(ge=0, le=100)
    channel_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    summary: str
    execution_priorities: list[str] = Field(default_factory=list)


class ContentGenerationEvaluation(BaseModel):
    project_id: str
    asset_title: str
    clarity_score: float = Field(ge=0, le=100)
    channel_fit_score: float = Field(ge=0, le=100)
    actionability_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    suggested_outline: list[str] = Field(default_factory=list)
    call_to_action: str = ""
    summary: str


BEST_AVAILABLE_TOOLS = {
    "frontend": ["Next.js App Router", "Turborepo"],
    "workflow_orchestration": ["Temporal", "LangGraph", "n8n"],
    "analytics": ["PostHog"],
    "content_platform": ["Sanity"],
    "ingestion": ["Unstructured", "Playwright", "Airbyte"],
}


def evaluate_marketing_research(project: MarketingProject, research: MarketingResearchRecord) -> MarketingResearchEvaluation:
    market_score = min(40 + len(research.market_summary) / 20, 100)
    competitor_score = min(35 + len(research.competitor_summary) / 20, 100)
    audience_score = min(30 + (len(research.audience_insights) * 12), 100)
    channel_score = min(30 + (len(research.channel_insights) * 12), 100)
    confidence_score = round((market_score * 0.25) + (competitor_score * 0.25) + (audience_score * 0.25) + (channel_score * 0.25), 2)
    priorities = []
    if audience_score < 60:
        priorities.append("Deepen audience interviews and segmentation.")
    if channel_score < 60:
        priorities.append("Validate highest-yield channels before execution.")
    if competitor_score < 60:
        priorities.append("Expand competitor and positioning analysis.")
    if not priorities:
        priorities.append("Move into channel-specific execution planning.")
    return MarketingResearchEvaluation(
        project_id=project.id,
        market_score=market_score,
        competitor_score=competitor_score,
        audience_score=audience_score,
        channel_score=channel_score,
        confidence_score=confidence_score,
        summary=f"Marketing research confidence scored {confidence_score:.1f}/100 for {project.name}.",
        execution_priorities=priorities,
    )


def evaluate_content_asset(project: MarketingProject, asset: ContentAsset) -> ContentGenerationEvaluation:
    clarity_score = min(40 + len(asset.source_brief) / 25 + len(asset.generated_outline) * 6, 100)
    channel_fit_score = 65 if asset.target_channel in project.channels else 45
    actionability_score = min(35 + len(asset.call_to_action) / 10 + len(asset.body) / 100, 100)
    confidence_score = round((clarity_score * 0.4) + (channel_fit_score * 0.25) + (actionability_score * 0.35), 2)
    suggested_outline = asset.generated_outline or [
        "Hook",
        "Problem or opportunity",
        "Evidence and positioning",
        "Recommendation or CTA",
    ]
    call_to_action = asset.call_to_action or "Schedule a review or next step."
    return ContentGenerationEvaluation(
        project_id=project.id,
        asset_title=asset.title,
        clarity_score=clarity_score,
        channel_fit_score=channel_fit_score,
        actionability_score=actionability_score,
        confidence_score=confidence_score,
        suggested_outline=suggested_outline,
        call_to_action=call_to_action,
        summary=f"Content asset {asset.title} scored {confidence_score:.1f}/100 for execution readiness.",
    )
