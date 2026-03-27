"""CLI for AI-Scientist-style research loop skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_loop import ResearchIdea, ResearchLoop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run research loop snapshot")
    parser.add_argument("--ideas", required=True, help="Path to ideas JSON")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--as-json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.ideas).read_text())

    loop = ResearchLoop()
    for idea_payload in payload:
        idea = ResearchIdea(**idea_payload)
        root = loop.add_root_idea(idea)
        loop.score_node(
            root.node_id,
            {
                "novelty": 0.6,
                "feasibility": 0.7,
                "signal_quality": 0.6,
                "safety": 0.9,
            },
        )

    frontier = [n.node_id for n in loop.select_frontier(top_k=args.top_k)]
    snapshot = loop.export_snapshot()
    snapshot["frontier"] = frontier

    if args.as_json:
        print(json.dumps(snapshot, indent=2))
    else:
        print(f"nodes: {snapshot['node_count']}")
        print(f"frontier: {frontier}")


if __name__ == "__main__":
    main()
