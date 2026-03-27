"""CLI for sprint-3 supply-chain controls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from supply_chain import PackageEntry, SupplyChainManager, VulnerabilityFinding


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supply-chain operations")
    sub = parser.add_subparsers(dest="command", required=True)

    sbom = sub.add_parser("sbom", help="Generate SBOM from packages JSON")
    sbom.add_argument("--project", required=True)
    sbom.add_argument("--packages", required=True, help="Path to packages JSON")

    prov = sub.add_parser("provenance", help="Generate provenance for an artifact")
    prov.add_argument("--build-id", required=True)
    prov.add_argument("--commit", required=True)
    prov.add_argument("--builder", required=True)
    prov.add_argument("--artifact", required=True)

    sla = sub.add_parser("sla", help="Evaluate vulnerability SLA")
    sla.add_argument("--findings", required=True, help="Path to findings JSON")
    sla.add_argument("--critical-max-days", type=int, default=7)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "sbom":
        payload = json.loads(Path(args.packages).read_text())
        packages = [PackageEntry(**item) for item in payload]
        sbom = SupplyChainManager.generate_sbom(packages, args.project)
        print(SupplyChainManager.to_json(sbom))
        return

    if args.command == "provenance":
        artifact = Path(args.artifact).read_bytes()
        provenance = SupplyChainManager.generate_provenance(
            build_id=args.build_id,
            commit_sha=args.commit,
            builder=args.builder,
            artifact_bytes=artifact,
        )
        print(SupplyChainManager.to_json(provenance))
        return

    if args.command == "sla":
        payload = json.loads(Path(args.findings).read_text())
        findings = [VulnerabilityFinding(**item) for item in payload]
        verdict = SupplyChainManager.evaluate_vulnerability_sla(
            findings, max_open_days_critical=args.critical_max_days
        )
        print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
