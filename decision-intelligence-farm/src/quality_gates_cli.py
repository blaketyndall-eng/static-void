"""CLI wrapper for sprint-2 quality gate checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quality_gates import ChangeEnvelope, QualityGatePolicy, RiskTier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate quality gates for a change")
    parser.add_argument("--input", required=True, help="Path to envelope JSON")
    parser.add_argument("--as-json", action="store_true")
    return parser.parse_args()


def load_envelope(path: str) -> ChangeEnvelope:
    payload = json.loads(Path(path).read_text())
    return ChangeEnvelope(
        risk_tier=RiskTier(payload["risk_tier"]),
        tests_passed=payload.get("tests_passed", False),
        lint_passed=payload.get("lint_passed", False),
        build_passed=payload.get("build_passed", False),
        observability_verified=payload.get("observability_verified", False),
        rollback_validated=payload.get("rollback_validated", False),
        critical_regression_tests_passed=payload.get(
            "critical_regression_tests_passed", False
        ),
        security_scan_passed=payload.get("security_scan_passed", True),
    )


def main() -> None:
    args = parse_args()
    envelope = load_envelope(args.input)
    result = QualityGatePolicy.evaluate(envelope)
    checklist = QualityGatePolicy.release_checklist(envelope)

    output = {
        "passed": result.passed,
        "failed_checks": result.failed_checks,
        "warnings": result.warnings,
        "checklist": checklist,
    }

    if args.as_json:
        print(json.dumps(output, indent=2))
    else:
        print(f"passed: {result.passed}")
        print(f"failed_checks: {result.failed_checks}")
        if result.warnings:
            print(f"warnings: {result.warnings}")


if __name__ == "__main__":
    main()
