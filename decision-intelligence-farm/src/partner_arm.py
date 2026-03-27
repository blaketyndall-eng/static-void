"""Partner Arm: partner scoring and expansion readiness."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PartnerProfile:
    name: str
    integration_effort: int  # 1 (easy) to 5 (hard)
    market_reach: int        # 1 (low) to 5 (high)
    reliability_score: float # 0-1


def partner_score(p: PartnerProfile) -> float:
    score = (p.market_reach * 0.4) + ((6 - p.integration_effort) * 0.3) + (p.reliability_score * 5 * 0.3)
    return round(score, 3)


def rank_partners(partners: list[PartnerProfile]) -> list[tuple[str, float]]:
    ranked = sorted(((p.name, partner_score(p)) for p in partners), key=lambda x: x[1], reverse=True)
    return ranked
