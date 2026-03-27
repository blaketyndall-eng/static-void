"""CLI for repository automation/intelligence audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from automation_intelligence_audit import RepoAutomationAudit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automation/intelligence audit")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--as-json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = RepoAutomationAudit(Path(args.repo_root).resolve())
    findings = audit.run()
    summary = audit.summary(findings)

    payload = {
        "summary": summary,
        "findings": [f.__dict__ for f in findings],
    }

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(summary, indent=2))
        for f in findings:
            print(f"- [{f.status}] {f.area}: {f.detail}")
            print(f"  -> {f.recommendation}")


if __name__ == "__main__":
    main()
