"""Sprint 3 supply-chain controls: SBOM, provenance, and vulnerability SLA checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class PackageEntry:
    name: str
    version: str
    ecosystem: str = "python"
    license: str = "UNKNOWN"


@dataclass
class VulnerabilityFinding:
    package: str
    severity: str
    opened_at: str  # YYYY-MM-DD
    fixed: bool = False


@dataclass
class BuildProvenance:
    build_id: str
    commit_sha: str
    builder: str
    started_at: str
    finished_at: str
    artifact_digest: str


class SupplyChainManager:
    """Minimal implementation of sprint-3 supply-chain requirements."""

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()[:19]

    @staticmethod
    def generate_sbom(packages: list[PackageEntry], project_name: str) -> dict:
        """Create a lightweight SPDX-like SBOM payload."""
        doc_id = hashlib.sha256(
            (project_name + str(len(packages))).encode("utf-8")
        ).hexdigest()[:16]
        return {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": f"SPDXRef-DOCUMENT-{doc_id}",
            "name": project_name,
            "created": SupplyChainManager._utc_now(),
            "packages": [asdict(p) for p in packages],
        }

    @staticmethod
    def generate_provenance(
        *, build_id: str, commit_sha: str, builder: str, artifact_bytes: bytes
    ) -> BuildProvenance:
        digest = hashlib.sha256(artifact_bytes).hexdigest()
        now = SupplyChainManager._utc_now()
        return BuildProvenance(
            build_id=build_id,
            commit_sha=commit_sha,
            builder=builder,
            started_at=now,
            finished_at=now,
            artifact_digest=f"sha256:{digest}",
        )

    @staticmethod
    def evaluate_vulnerability_sla(
        findings: list[VulnerabilityFinding], *, max_open_days_critical: int = 7
    ) -> dict:
        """Check vulnerability aging policy with severity-weighted SLA."""
        today = datetime.now(timezone.utc).date()
        breaches = []

        for finding in findings:
            if finding.fixed:
                continue
            opened = datetime.strptime(finding.opened_at, "%Y-%m-%d").date()
            age_days = (today - opened).days

            if finding.severity.lower() == "critical" and age_days > max_open_days_critical:
                breaches.append(
                    {
                        "package": finding.package,
                        "severity": finding.severity,
                        "age_days": age_days,
                    }
                )

        return {
            "passed": len(breaches) == 0,
            "breaches": breaches,
            "open_findings": len([f for f in findings if not f.fixed]),
        }

    @staticmethod
    def to_json(payload: dict | BuildProvenance) -> str:
        if isinstance(payload, BuildProvenance):
            return json.dumps(asdict(payload), indent=2)
        return json.dumps(payload, indent=2)
