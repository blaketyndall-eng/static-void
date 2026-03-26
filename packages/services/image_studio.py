from pydantic import BaseModel, Field

from packages.domain.image_studio import (
    ImageStudioRenderJob,
    ImageStudioReview,
    ImageStudioSnapshot,
    ImageStudioWorkspace,
)


class ImageStudioPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_creative_reliability_score: float
    average_deployment_readiness_score: float
    top_generation_modes: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_IMAGE_STUDIO_ACTIONS = [
    'Define model registry ownership and approved generation modes.',
    'Create prompt recipes, control profiles, and edit profiles for repeatable work.',
    'Track artifact outputs and variant scoring rules for every creative experiment.',
]


def review_image_studio_workspace(
    workspace: ImageStudioWorkspace,
    snapshot: ImageStudioSnapshot | None,
) -> ImageStudioReview:
    reliability = snapshot.creative_reliability_score if snapshot is not None else 25.0
    readiness = snapshot.deployment_readiness_score if snapshot is not None else 25.0
    studio_readiness = round(
        min(
            30 + len(workspace.creative_domains) * 6 + len(workspace.output_goals) * 6 + (0 if snapshot is None else len(snapshot.generation_modes) * 4),
            100,
        ),
        2,
    )
    review_score = round((reliability * 0.35) + (readiness * 0.35) + (studio_readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial image studio snapshot.')
    if not workspace.creative_domains:
        actions.append('Define the creative domains this studio supports.')
    if not workspace.output_goals:
        actions.append('Define explicit creative output goals and success criteria.')
    if snapshot is not None and snapshot.opportunities:
        actions.append('Prioritize the highest-value creative opportunity first.')
    actions.extend(DEFAULT_IMAGE_STUDIO_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return ImageStudioReview(
        workspace_id=workspace.id,
        review_score=review_score,
        studio_readiness=studio_readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on image studio readiness.',
    )


class ImageStudioRenderJobSummary(BaseModel):
    workspace_id: str
    queued_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    recent_modes: list[str] = Field(default_factory=list)


def build_image_studio_summary(
    workspaces: list[ImageStudioWorkspace],
    snapshots: dict[str, ImageStudioSnapshot],
) -> ImageStudioPortfolioSummary:
    if not workspaces:
        return ImageStudioPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_creative_reliability_score=0.0,
            average_deployment_readiness_score=0.0,
        )

    active_count = 0
    reliability_scores = []
    readiness_scores = []
    mode_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            reliability_scores.append(snapshot.creative_reliability_score)
            readiness_scores.append(snapshot.deployment_readiness_score)
            for mode in snapshot.generation_modes:
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_reliability = round(sum(reliability_scores) / len(reliability_scores), 2) if reliability_scores else 0.0
    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 2) if readiness_scores else 0.0
    top_generation_modes = [item for item, _count in sorted(mode_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return ImageStudioPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_creative_reliability_score=avg_reliability,
        average_deployment_readiness_score=avg_readiness,
        top_generation_modes=top_generation_modes,
        top_opportunities=top_opportunities,
    )


def build_render_job_summary(workspace_id: str, jobs: list[ImageStudioRenderJob]) -> ImageStudioRenderJobSummary:
    queued = sum(1 for job in jobs if job.status == 'queued')
    running = sum(1 for job in jobs if job.status == 'running')
    completed = sum(1 for job in jobs if job.status == 'completed')
    failed = sum(1 for job in jobs if job.status == 'failed')
    recent_modes = list(dict.fromkeys([job.mode for job in jobs[:10]]))[:5]
    return ImageStudioRenderJobSummary(
        workspace_id=workspace_id,
        queued_jobs=queued,
        running_jobs=running,
        completed_jobs=completed,
        failed_jobs=failed,
        recent_modes=recent_modes,
    )
