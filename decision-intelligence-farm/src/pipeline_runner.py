"""Sprint 11: simple pipeline orchestration runtime."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PipelineStep:
    name: str
    status: str = "pending"
    detail: str = ""


@dataclass
class PipelineRun:
    run_id: str
    steps: list[PipelineStep] = field(default_factory=list)

    def mark(self, step_name: str, status: str, detail: str = "") -> None:
        for step in self.steps:
            if step.name == step_name:
                step.status = status
                step.detail = detail
                return
        self.steps.append(PipelineStep(name=step_name, status=status, detail=detail))

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "total_steps": len(self.steps),
            "passed": len([s for s in self.steps if s.status == "passed"]),
            "failed": len([s for s in self.steps if s.status == "failed"]),
            "pending": len([s for s in self.steps if s.status == "pending"]),
        }
