"""Detect trend regressions across dashboard snapshots."""

from __future__ import annotations


def detect_ai_eval_drift(previous: dict, current: dict, threshold: float = 0.05) -> dict:
    prev_pass = previous.get("pass_rate", 0.0)
    curr_pass = current.get("pass_rate", 0.0)
    delta = round(curr_pass - prev_pass, 3)
    return {
        "previous_pass_rate": prev_pass,
        "current_pass_rate": curr_pass,
        "delta": delta,
        "regression": delta < -threshold,
    }


def detect_delivery_drift(previous: dict, current: dict, threshold: float = 0.05) -> dict:
    prev_delivery = previous.get("delivery_rate", 0.0)
    curr_delivery = current.get("delivery_rate", 0.0)
    delta = round(curr_delivery - prev_delivery, 3)
    return {
        "previous_delivery_rate": prev_delivery,
        "current_delivery_rate": curr_delivery,
        "delta": delta,
        "regression": delta < -threshold,
    }
