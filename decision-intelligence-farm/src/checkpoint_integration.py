"""Next major checkpoint: integrate specialized arms into one flow."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_registry import ArtifactRegistry
from customer_intelligence import CustomerIntelligence, FeedbackItem
from model_ops import evaluate_model_release
from promotion_engine import should_promote_release
from revenue_gtm import GTMExperiment


THEME_TO_EXPERIMENT = {
    "pricing": ("pricing-test", "pricing-page"),
    "usability": ("ux-onboarding", "product"),
    "performance": ("speed-landing", "product"),
    "trust": ("accuracy-proof", "content"),
    "other": ("message-clarity", "landing"),
}


def build_experiment_backlog(items: list[FeedbackItem], default_spend: float = 100.0) -> list[GTMExperiment]:
    themes = CustomerIntelligence.top_opportunities(items, top_k=5)
    backlog: list[GTMExperiment] = []
    for theme, count in themes:
        name, channel = THEME_TO_EXPERIMENT.get(theme, THEME_TO_EXPERIMENT["other"])
        backlog.append(
            GTMExperiment(
                name=f"{name}-{count}",
                channel=channel,
                spend=default_spend,
                revenue=0.0,
                conversion_rate=0.0,
            )
        )
    return backlog


def persist_customer_snapshot(registry_dir: str | Path, feedback: list[FeedbackItem]) -> Path:
    registry = ArtifactRegistry(Path(registry_dir))
    payload = CustomerIntelligence.summarize(feedback)
    payload["top_opportunities"] = CustomerIntelligence.top_opportunities(feedback)
    return registry.register("customer_signals", payload)


def persist_gtm_backlog(registry_dir: str | Path, backlog: list[GTMExperiment]) -> Path:
    registry = ArtifactRegistry(Path(registry_dir))
    payload = {"experiments": [e.__dict__ for e in backlog]}
    return registry.register("gtm_backlog", payload)


def promotion_decision_with_model_ops(
    *,
    quality_passed: bool,
    supply_chain_passed: bool,
    baseline_pass_rate: float,
    candidate_pass_rate: float,
    safety_incidents: int,
    delivery_rate: float,
) -> dict:
    model_verdict = evaluate_model_release(
        baseline_pass_rate=baseline_pass_rate,
        candidate_pass_rate=candidate_pass_rate,
        safety_incidents=safety_incidents,
    )

    # hard gate: model verdict must allow promotion
    decision = should_promote_release(
        quality_passed=quality_passed,
        supply_chain_passed=supply_chain_passed,
        ai_eval_pass_rate=candidate_pass_rate,
        delivery_rate=delivery_rate,
    )

    if not model_verdict["promote"]:
        decision["promote"] = False
        decision["blocked_reasons"].extend(model_verdict["reasons"])

    decision["model_ops"] = model_verdict
    return decision


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())
