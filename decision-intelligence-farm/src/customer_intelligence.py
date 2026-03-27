"""Customer Intelligence Arm: ingest, classify, and prioritize market signals."""

from __future__ import annotations

from dataclasses import dataclass
from collections import Counter


@dataclass
class FeedbackItem:
    source: str
    text: str
    segment: str = "unknown"


class CustomerIntelligence:
    KEYWORDS = {
        "pricing": ["price", "pricing", "cost", "expensive"],
        "usability": ["confusing", "hard", "ux", "interface"],
        "performance": ["slow", "latency", "fast", "speed"],
        "trust": ["wrong", "accuracy", "trust", "reliable"],
    }

    @classmethod
    def classify(cls, item: FeedbackItem) -> str:
        text = item.text.lower()
        for label, terms in cls.KEYWORDS.items():
            if any(t in text for t in terms):
                return label
        return "other"

    @classmethod
    def summarize(cls, items: list[FeedbackItem]) -> dict:
        labels = [cls.classify(i) for i in items]
        by_label = Counter(labels)
        by_segment = Counter(i.segment for i in items)
        return {
            "total_feedback": len(items),
            "themes": dict(by_label),
            "segments": dict(by_segment),
        }

    @classmethod
    def top_opportunities(cls, items: list[FeedbackItem], top_k: int = 3) -> list[tuple[str, int]]:
        themes = Counter(cls.classify(i) for i in items)
        return themes.most_common(top_k)
