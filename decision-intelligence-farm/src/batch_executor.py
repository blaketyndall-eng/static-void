"""Sprint 14: lightweight batch execution planner."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BatchJob:
    job_id: str
    priority: int
    estimated_minutes: int


def plan_batches(jobs: list[BatchJob], max_minutes_per_batch: int = 60) -> list[list[BatchJob]]:
    """Greedy binning by priority then fit-by-time."""
    ordered = sorted(jobs, key=lambda j: (-j.priority, j.estimated_minutes))
    batches: list[list[BatchJob]] = []

    for job in ordered:
        placed = False
        for batch in batches:
            total = sum(x.estimated_minutes for x in batch)
            if total + job.estimated_minutes <= max_minutes_per_batch:
                batch.append(job)
                placed = True
                break
        if not placed:
            batches.append([job])

    return batches
