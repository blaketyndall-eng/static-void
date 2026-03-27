"""Sprint 5 operating cadence and capability scorecard utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CapabilityScore:
    track: str
    level: str
    evidence_count: int
    delivery_score: float
    quality_score: float


@dataclass
class JourneyUXMetric:
    journey: str
    baseline_success_rate: float
    current_success_rate: float
    baseline_completion_minutes: float
    current_completion_minutes: float


class Sprint5Ops:
    """Utilities for quarterly capability and UX maturity checks."""

    @staticmethod
    def capability_health(scores: list[CapabilityScore]) -> dict:
        if not scores:
            return {
                "tracks": 0,
                "avg_delivery": 0.0,
                "avg_quality": 0.0,
                "advancement_ready_tracks": [],
            }

        avg_delivery = sum(s.delivery_score for s in scores) / len(scores)
        avg_quality = sum(s.quality_score for s in scores) / len(scores)
        ready = [
            s.track
            for s in scores
            if s.evidence_count >= 3 and s.delivery_score >= 0.75 and s.quality_score >= 0.75
        ]
        return {
            "tracks": len(scores),
            "avg_delivery": round(avg_delivery, 3),
            "avg_quality": round(avg_quality, 3),
            "advancement_ready_tracks": ready,
        }

    @staticmethod
    def ux_improvement_report(metrics: list[JourneyUXMetric]) -> dict:
        if not metrics:
            return {"journeys": 0, "success_lift": 0.0, "time_reduction": 0.0}

        success_lift = sum(
            m.current_success_rate - m.baseline_success_rate for m in metrics
        ) / len(metrics)
        time_reduction = sum(
            m.baseline_completion_minutes - m.current_completion_minutes for m in metrics
        ) / len(metrics)

        improved = [
            m.journey
            for m in metrics
            if m.current_success_rate >= m.baseline_success_rate
            and m.current_completion_minutes <= m.baseline_completion_minutes
        ]

        return {
            "journeys": len(metrics),
            "success_lift": round(success_lift, 3),
            "time_reduction": round(time_reduction, 3),
            "fully_improved_journeys": improved,
        }

    @staticmethod
    def onboarding_readiness(days_to_productive: int) -> dict:
        return {
            "days_to_productive": days_to_productive,
            "target_days": 14,
            "meets_target": days_to_productive <= 14,
        }
