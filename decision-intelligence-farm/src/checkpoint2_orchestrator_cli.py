"""CLI for weekly loop orchestrator checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from checkpoint2_orchestrator import WeeklyLoopOrchestrator
from customer_intelligence import FeedbackItem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly loop orchestrator")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--registry-dir", required=True)
    parser.add_argument("--quality-passed", action="store_true")
    parser.add_argument("--supply-chain-passed", action="store_true")
    parser.add_argument("--baseline-pass-rate", type=float, default=0.9)
    parser.add_argument("--candidate-pass-rate", type=float, default=0.9)
    parser.add_argument("--safety-incidents", type=int, default=0)
    parser.add_argument("--delivery-rate", type=float, default=0.8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.feedback).read_text())
    feedback = [FeedbackItem(**x) for x in payload]

    out = WeeklyLoopOrchestrator(args.registry_dir).run(
        run_id=args.run_id,
        feedback=feedback,
        quality_passed=args.quality_passed,
        supply_chain_passed=args.supply_chain_passed,
        baseline_pass_rate=args.baseline_pass_rate,
        candidate_pass_rate=args.candidate_pass_rate,
        safety_incidents=args.safety_incidents,
        delivery_rate=args.delivery_rate,
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
