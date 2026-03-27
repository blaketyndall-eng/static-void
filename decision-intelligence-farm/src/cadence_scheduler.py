"""Schedule weekly/biweekly/monthly governance tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class CadenceTask:
    name: str
    frequency: str
    next_due: str


class CadenceScheduler:
    @staticmethod
    def build_schedule(today: date) -> list[CadenceTask]:
        weekly = today + timedelta(days=(4 - today.weekday()) % 7)  # Friday
        biweekly = weekly + timedelta(days=14)
        monthly = date(today.year, today.month, 28)
        while monthly.weekday() != 4:
            monthly += timedelta(days=1)
            if monthly.month != today.month:
                monthly -= timedelta(days=1)
                break

        return [
            CadenceTask("weekly_execution_review", "weekly", weekly.isoformat()),
            CadenceTask("biweekly_capability_review", "biweekly", biweekly.isoformat()),
            CadenceTask("monthly_risk_review", "monthly", monthly.isoformat()),
        ]
