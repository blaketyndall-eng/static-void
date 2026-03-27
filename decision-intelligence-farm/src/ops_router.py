"""Unified CLI router to reduce operator friction across modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_eval import AIEvalHarness, EvalCase
from automation_intelligence_audit import RepoAutomationAudit
from quality_gates import ChangeEnvelope, QualityGatePolicy, RiskTier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Ops Router")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Run repo automation audit")
    audit.add_argument("--repo-root", default=".")

    gate = sub.add_parser("gate", help="Run quality gate check")
    gate.add_argument("--input", required=True, help="Path to quality gate envelope JSON")

    evalp = sub.add_parser("eval", help="Run AI eval summary")
    evalp.add_argument("--cases", required=True)
    evalp.add_argument("--outputs", required=True)

    return parser.parse_args()


def run() -> dict:
    args = parse_args()

    if args.command == "audit":
        audit = RepoAutomationAudit(Path(args.repo_root).resolve())
        findings = audit.run()
        return {
            "summary": audit.summary(findings),
            "findings": [f.__dict__ for f in findings],
        }

    if args.command == "gate":
        payload = json.loads(Path(args.input).read_text())
        envelope = ChangeEnvelope(
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
        result = QualityGatePolicy.evaluate(envelope)
        return {
            "passed": result.passed,
            "failed_checks": result.failed_checks,
            "warnings": result.warnings,
        }

    if args.command == "eval":
        raw_cases = json.loads(Path(args.cases).read_text())
        raw_outputs = json.loads(Path(args.outputs).read_text())
        by_id = {o["case_id"]: o["output"] for o in raw_outputs}
        results = [
            AIEvalHarness.evaluate_case(EvalCase(**case), by_id.get(case["case_id"], ""))
            for case in raw_cases
        ]
        return {
            "summary": AIEvalHarness.summarize(results),
            "results": [r.__dict__ for r in results],
        }

    return {"error": "unknown command"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
