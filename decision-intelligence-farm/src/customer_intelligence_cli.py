"""CLI for Customer Intelligence Arm."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from customer_intelligence import CustomerIntelligence, FeedbackItem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Customer intelligence summarizer")
    parser.add_argument("--feedback", required=True, help="Path to feedback JSON")
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.feedback).read_text())
    items = [FeedbackItem(**x) for x in payload]
    summary = CustomerIntelligence.summarize(items)
    summary["top_opportunities"] = CustomerIntelligence.top_opportunities(items, top_k=args.top_k)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
