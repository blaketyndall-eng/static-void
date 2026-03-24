from pydantic import BaseModel, Field

from packages.domain.investment import InvestmentThesis


class PortfolioRiskSnapshot(BaseModel):
    total_theses: int
    active_count: int
    by_asset_class: dict[str, int] = Field(default_factory=dict)
    by_timeframe: dict[str, int] = Field(default_factory=dict)
    crowded_asset_classes: list[str] = Field(default_factory=list)
    crowded_timeframes: list[str] = Field(default_factory=list)
    overlap_flags: list[str] = Field(default_factory=list)
    risk_pressure_score: float = Field(default=0.0, ge=0, le=100)


CATEGORY_LIQUIDITY_FLOORS = {
    "equity": 45.0,
    "option": 60.0,
    "crypto": 55.0,
    "prediction_market": 40.0,
}


def build_portfolio_risk_snapshot(theses: list[InvestmentThesis]) -> PortfolioRiskSnapshot:
    by_asset_class: dict[str, int] = {}
    by_timeframe: dict[str, int] = {}
    active = [thesis for thesis in theses if thesis.status.value in {"active", "scaling"}]

    for thesis in theses:
        asset_class = thesis.asset_class.value
        timeframe = thesis.timeframe
        by_asset_class[asset_class] = by_asset_class.get(asset_class, 0) + 1
        by_timeframe[timeframe] = by_timeframe.get(timeframe, 0) + 1

    crowded_asset_classes = [key for key, value in by_asset_class.items() if value >= 3]
    crowded_timeframes = [key for key, value in by_timeframe.items() if value >= 3]

    overlap_flags: list[str] = []
    for asset_class in crowded_asset_classes:
        overlap_flags.append(f"crowded_asset_class:{asset_class}")
    for timeframe in crowded_timeframes:
        overlap_flags.append(f"crowded_timeframe:{timeframe}")

    risk_pressure_score = 25.0
    risk_pressure_score += min(len(active) * 7, 25)
    risk_pressure_score += min(len(crowded_asset_classes) * 10, 20)
    risk_pressure_score += min(len(crowded_timeframes) * 6, 15)
    risk_pressure_score = max(0.0, min(risk_pressure_score, 100.0))

    return PortfolioRiskSnapshot(
        total_theses=len(theses),
        active_count=len(active),
        by_asset_class=by_asset_class,
        by_timeframe=by_timeframe,
        crowded_asset_classes=crowded_asset_classes,
        crowded_timeframes=crowded_timeframes,
        overlap_flags=overlap_flags,
        risk_pressure_score=round(risk_pressure_score, 2),
    )
