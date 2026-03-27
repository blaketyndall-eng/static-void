"""Sprint 15: release promotion decisions using governance signals."""

from __future__ import annotations


def should_promote_release(
    *,
    quality_passed: bool,
    supply_chain_passed: bool,
    ai_eval_pass_rate: float,
    min_ai_eval_pass_rate: float = 0.85,
    delivery_rate: float = 0.7,
) -> dict:
    blocked_reasons = []

    if not quality_passed:
        blocked_reasons.append("quality gate failed")
    if not supply_chain_passed:
        blocked_reasons.append("supply-chain checks failed")
    if ai_eval_pass_rate < min_ai_eval_pass_rate:
        blocked_reasons.append("ai eval below threshold")
    if delivery_rate < 0.5:
        blocked_reasons.append("delivery health too low")

    return {
        "promote": len(blocked_reasons) == 0,
        "blocked_reasons": blocked_reasons,
    }
