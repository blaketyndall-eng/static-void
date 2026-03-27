"""AI-Scientist-inspired research loop for the Decision Intelligence farm.

Implements a safe, lightweight adaptation of the ideation -> experiment ->
review cycle by orchestrating existing local modules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class ResearchIdea:
    name: str
    title: str
    hypothesis: str
    experiments: list[str]
    risk_factors: list[str]


@dataclass
class ResearchNode:
    node_id: str
    idea: ResearchIdea
    parent_id: str | None = None
    score: float = 0.0
    status: str = "proposed"


class ResearchLoop:
    """Small best-first loop skeleton inspired by AI-Scientist-v2 orchestration."""

    def __init__(self):
        self.nodes: dict[str, ResearchNode] = {}

    def add_root_idea(self, idea: ResearchIdea) -> ResearchNode:
        node_id = f"root_{idea.name}"
        node = ResearchNode(node_id=node_id, idea=idea, parent_id=None)
        self.nodes[node_id] = node
        return node

    def branch_node(self, parent_id: str, variant_suffix: str, tweak: str) -> ResearchNode:
        parent = self.nodes[parent_id]
        node_id = f"{parent_id}_{variant_suffix}"
        branched = ResearchIdea(
            name=f"{parent.idea.name}_{variant_suffix}",
            title=f"{parent.idea.title} ({variant_suffix})",
            hypothesis=f"{parent.idea.hypothesis} | tweak: {tweak}",
            experiments=parent.idea.experiments,
            risk_factors=parent.idea.risk_factors,
        )
        node = ResearchNode(node_id=node_id, idea=branched, parent_id=parent_id)
        self.nodes[node_id] = node
        return node

    def score_node(self, node_id: str, metrics: dict[str, float]) -> float:
        """Weighted score for prioritizing next expansion/debug/review."""
        score = (
            metrics.get("novelty", 0) * 0.35
            + metrics.get("feasibility", 0) * 0.25
            + metrics.get("signal_quality", 0) * 0.25
            + metrics.get("safety", 0) * 0.15
        )
        self.nodes[node_id].score = round(score, 3)
        return self.nodes[node_id].score

    def select_frontier(self, top_k: int = 3) -> list[ResearchNode]:
        ranked = sorted(self.nodes.values(), key=lambda n: n.score, reverse=True)
        return ranked[:top_k]

    def mark_status(self, node_id: str, status: str) -> None:
        self.nodes[node_id].status = status

    def export_snapshot(self) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat()[:19],
            "node_count": len(self.nodes),
            "nodes": [asdict(n) for n in self.nodes.values()],
        }
