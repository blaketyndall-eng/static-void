"""Repository automation/intelligence audit for sprint-5 review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditFinding:
    area: str
    status: str
    detail: str
    recommendation: str


class RepoAutomationAudit:
    """Heuristic repo scan to identify automation + intelligence opportunities."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src = repo_root / "decision-intelligence-farm" / "src"
        self.docs = repo_root / "docs" / "decision-intelligence-console"

    def run(self) -> list[AuditFinding]:
        findings: list[AuditFinding] = []

        test_files = sorted(self.src.glob("test_*.py"))
        cli_files = sorted(self.src.glob("*_cli.py"))

        findings.append(
            AuditFinding(
                area="test_coverage_surface",
                status="good" if len(test_files) >= 4 else "partial",
                detail=f"Detected {len(test_files)} test files.",
                recommendation="Add CI test discovery + thresholds per module risk tier.",
            )
        )

        findings.append(
            AuditFinding(
                area="operator_interfaces",
                status="good" if len(cli_files) >= 4 else "partial",
                detail=f"Detected {len(cli_files)} CLI entry points.",
                recommendation="Unify CLIs under one top-level command router for automation.",
            )
        )

        ci_files = list(self.repo_root.glob(".github/workflows/*.yml")) + list(
            self.repo_root.glob(".github/workflows/*.yaml")
        )
        findings.append(
            AuditFinding(
                area="ci_automation",
                status="missing" if not ci_files else "present",
                detail="No GitHub Actions workflows detected."
                if not ci_files
                else f"Detected {len(ci_files)} workflow file(s).",
                recommendation="Add CI workflows for tests, lint, security scans, and release checks.",
            )
        )

        design_docs = list(self.docs.glob("*.md"))
        findings.append(
            AuditFinding(
                area="operating_docs",
                status="good" if len(design_docs) >= 10 else "partial",
                detail=f"Detected {len(design_docs)} markdown docs in console package.",
                recommendation="Auto-generate status dashboards from scorecard/eval artifacts.",
            )
        )

        return findings

    @staticmethod
    def summary(findings: list[AuditFinding]) -> dict:
        by_status = {"good": 0, "partial": 0, "missing": 0, "present": 0}
        for finding in findings:
            by_status[finding.status] = by_status.get(finding.status, 0) + 1

        priorities = [
            f.recommendation for f in findings if f.status in {"missing", "partial"}
        ]

        return {
            "areas": len(findings),
            "status_counts": by_status,
            "priority_recommendations": priorities,
        }
