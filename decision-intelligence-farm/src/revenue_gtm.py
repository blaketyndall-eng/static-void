"""Revenue/GTM Experiment Arm: track and rank commercial experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GTMExperiment:
    name: str
    channel: str
    spend: float
    revenue: float
    conversion_rate: float

    @property
    def roi(self) -> float:
        if self.spend <= 0:
            return 0.0
        return round((self.revenue - self.spend) / self.spend, 3)


def rank_experiments(experiments: list[GTMExperiment]) -> list[GTMExperiment]:
    return sorted(experiments, key=lambda e: (e.roi, e.conversion_rate), reverse=True)


def summarize_experiments(experiments: list[GTMExperiment]) -> dict:
    if not experiments:
        return {"count": 0, "avg_roi": 0.0, "best": None}
    ranked = rank_experiments(experiments)
    return {
        "count": len(experiments),
        "avg_roi": round(sum(e.roi for e in experiments) / len(experiments), 3),
        "best": ranked[0].name,
    }
