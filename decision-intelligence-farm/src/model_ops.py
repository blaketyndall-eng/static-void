"""Model Ops Arm: model release gating and regression checks."""

from __future__ import annotations


def evaluate_model_release(
    *,
    baseline_pass_rate: float,
    candidate_pass_rate: float,
    safety_incidents: int,
    max_drop: float = 0.03,
) -> dict:
    drop = round(baseline_pass_rate - candidate_pass_rate, 3)
    blocked = drop > max_drop or safety_incidents > 0
    reasons = []
    if drop > max_drop:
        reasons.append("evaluation regression beyond threshold")
    if safety_incidents > 0:
        reasons.append("safety incidents detected")
    return {
        "promote": not blocked,
        "drop": drop,
        "reasons": reasons,
    }
