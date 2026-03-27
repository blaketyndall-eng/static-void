"""Sprint 13: recommendation engine for governance actions."""

from __future__ import annotations


def recommend_actions(dashboard: dict) -> list[str]:
    actions: list[str] = []
    alerts = dashboard.get("alerts", {})

    if alerts.get("quality_gate_failed"):
        actions.append("Block release and open regression triage within 24h.")
    if alerts.get("supply_chain_breach"):
        actions.append("Trigger security patch lane and vulnerability SLA review.")
    if alerts.get("ai_eval_regression"):
        actions.append("Run targeted AI eval debug set and freeze model promotion.")
    if alerts.get("automation_gap"):
        actions.append("Schedule automation gap closure sprint and assign owner.")

    if not actions:
        actions.append("No critical actions. Continue weekly cadence and monitor trends.")

    return actions
