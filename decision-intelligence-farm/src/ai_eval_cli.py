"""CLI for sprint-4 AI eval harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_eval import AIEvalHarness, EvalCase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI eval harness")
    parser.add_argument("--cases", required=True, help="Path to eval cases JSON")
    parser.add_argument("--outputs", required=True, help="Path to model outputs JSON")
    parser.add_argument("--as-json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_cases = json.loads(Path(args.cases).read_text())
    raw_outputs = json.loads(Path(args.outputs).read_text())

    outputs_by_id = {item["case_id"]: item["output"] for item in raw_outputs}

    results = []
    for item in raw_cases:
        case = EvalCase(**item)
        output = outputs_by_id.get(case.case_id, "")
        results.append(AIEvalHarness.evaluate_case(case, output))

    summary = AIEvalHarness.summarize(results)
    payload = {
        "summary": summary,
        "results": [r.__dict__ for r in results],
    }

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"cases: {summary['cases']}")
        print(f"pass_rate: {summary['pass_rate']}")
        print(f"avg_keyword_hit_rate: {summary['avg_keyword_hit_rate']}")
        print(f"refusal_rate: {summary['refusal_rate']}")


if __name__ == "__main__":
    main()
