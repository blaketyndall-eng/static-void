from pydantic import BaseModel, Field

from packages.domain.signals_forecasting import (
    SignalsForecastingReview,
    SignalsForecastingSnapshot,
    SignalsForecastingWorkspace,
)


class SignalsForecastingPortfolioSummary(BaseModel):
    workspace_count: int
    active_count: int
    average_signal_quality_score: float
    average_forecast_confidence_score: float
    top_risks: list[str] = Field(default_factory=list)
    top_opportunities: list[str] = Field(default_factory=list)


DEFAULT_SIGNAL_ACTIONS = [
    'Define baseline tracked domains and leading indicators.',
    'Create forecast hypotheses with review cadence.',
    'Set anomaly and regime-shift alert thresholds.',
]


def review_signals_forecasting_workspace(
    workspace: SignalsForecastingWorkspace,
    snapshot: SignalsForecastingSnapshot | None,
) -> SignalsForecastingReview:
    signal_quality = snapshot.signal_quality_score if snapshot is not None else 25.0
    forecast_confidence = snapshot.forecast_confidence_score if snapshot is not None else 25.0
    readiness = round(
        min(
            30 + len(workspace.tracked_domains) * 6 + len(workspace.forecast_targets) * 6 + (0 if snapshot is None else len(snapshot.trend_signals) * 4),
            100,
        ),
        2,
    )
    review_score = round((signal_quality * 0.35) + (forecast_confidence * 0.35) + (readiness * 0.3), 2)

    actions = []
    if snapshot is None:
        actions.append('Create an initial signal and forecast snapshot.')
    if not workspace.tracked_domains:
        actions.append('Define tracked domains and core leading indicators.')
    if not workspace.forecast_targets:
        actions.append('Define explicit forecast targets.')
    if snapshot is not None and snapshot.risks:
        actions.append('Reduce the highest-risk signal reliability issue first.')
    actions.extend(DEFAULT_SIGNAL_ACTIONS[:2])
    actions = list(dict.fromkeys(actions))[:5]

    return SignalsForecastingReview(
        workspace_id=workspace.id,
        review_score=review_score,
        signal_readiness=readiness,
        top_actions=actions,
        summary=f'{workspace.name} scored {review_score:.1f}/100 on signals and forecasting readiness.',
    )


def build_signals_forecasting_summary(
    workspaces: list[SignalsForecastingWorkspace],
    snapshots: dict[str, SignalsForecastingSnapshot],
) -> SignalsForecastingPortfolioSummary:
    if not workspaces:
        return SignalsForecastingPortfolioSummary(
            workspace_count=0,
            active_count=0,
            average_signal_quality_score=0.0,
            average_forecast_confidence_score=0.0,
        )

    active_count = 0
    signal_scores = []
    forecast_scores = []
    risk_counts: dict[str, int] = {}
    opportunity_counts: dict[str, int] = {}
    for workspace in workspaces:
        if workspace.status.value in {'active', 'monitoring'}:
            active_count += 1
        snapshot = snapshots.get(workspace.id)
        if snapshot is not None:
            signal_scores.append(snapshot.signal_quality_score)
            forecast_scores.append(snapshot.forecast_confidence_score)
            for risk in snapshot.risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            for opportunity in snapshot.opportunities:
                opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1

    avg_signal = round(sum(signal_scores) / len(signal_scores), 2) if signal_scores else 0.0
    avg_forecast = round(sum(forecast_scores) / len(forecast_scores), 2) if forecast_scores else 0.0
    top_risks = [item for item, _count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    top_opportunities = [item for item, _count in sorted(opportunity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    return SignalsForecastingPortfolioSummary(
        workspace_count=len(workspaces),
        active_count=active_count,
        average_signal_quality_score=avg_signal,
        average_forecast_confidence_score=avg_forecast,
        top_risks=top_risks,
        top_opportunities=top_opportunities,
    )
