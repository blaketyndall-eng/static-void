"""Data Reliability Arm: basic quality checks and trust scoring."""

from __future__ import annotations


def check_completeness(rows: list[dict], required_fields: list[str]) -> dict:
    if not rows:
        return {"rows": 0, "complete_ratio": 0.0}
    complete = 0
    for row in rows:
        if all(row.get(f) not in (None, "") for f in required_fields):
            complete += 1
    return {"rows": len(rows), "complete_ratio": round(complete / len(rows), 3)}


def check_freshness(latest_age_hours: float, max_age_hours: float = 24.0) -> dict:
    return {
        "latest_age_hours": latest_age_hours,
        "max_age_hours": max_age_hours,
        "fresh": latest_age_hours <= max_age_hours,
    }
