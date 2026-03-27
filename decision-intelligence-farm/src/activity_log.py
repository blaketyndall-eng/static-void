"""
The Farm Ledger — a running log of everything that happens on the farm.

Every piece of knowledge learned, every seed evolved, every milestone hit,
every trick taught to the dog, every decision made. This is the Farmer's
journal of EVENTS — not opinions, not notes, but what actually happened.

Blake can pull this up anytime to see what's been going on. The Farmer
can review it to refresh his memory. It's the ground truth timeline.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

import config

# ── Models ───────────────────────────────────────────────────────────

class LogEntry(BaseModel):
    """A single event in the farm's history."""
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()[:19]
    )
    category: str          # knowledge, seed, milestone, dog, decision, reflection, skill, tool, budget, execution
    event: str             # short event type: "learned", "evolved", "achieved", "taught", etc.
    title: str             # human-readable summary
    detail: str = ""       # optional longer description
    tags: list[str] = Field(default_factory=list)


class ActivityLog:
    """
    Append-only event log for the farm.

    Persists to a JSONL file (one JSON object per line) for efficient
    appending without needing to read/parse the whole file.
    """

    LOG_FILE = config.META_DIR / "activity_log.jsonl"

    def __init__(self):
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # ── Write ─────────────────────────────────────────────────

    def log(self, category: str, event: str, title: str,
            detail: str = "", tags: list[str] = None):
        """Append an event to the log."""
        entry = LogEntry(
            category=category,
            event=event,
            title=title,
            detail=detail,
            tags=tags or [],
        )
        with open(self.LOG_FILE, "a") as f:
            f.write(entry.model_dump_json() + "\n")

    # Convenience methods
    def log_knowledge(self, title: str, detail: str = "", tags: list[str] = None):
        self.log("knowledge", "learned", title, detail, tags)

    def log_seed_evolution(self, seed_name: str, detail: str = ""):
        self.log("seed", "evolved", f"{seed_name} seed evolved", detail, [seed_name])

    def log_milestone(self, milestone_name: str, detail: str = ""):
        self.log("milestone", "achieved", f"Milestone: {milestone_name}", detail, ["milestone"])

    def log_dog_trick(self, dog_name: str, trick_name: str):
        self.log("dog", "taught", f"{dog_name} learned '{trick_name}'", "", ["dog", trick_name])

    def log_reflection(self, detail: str = ""):
        self.log("reflection", "reflected", "Reflection cycle completed", detail, ["reflection"])

    def log_skill(self, skill_name: str, event: str, detail: str = ""):
        self.log("skill", event, f"Skill: {skill_name} — {event}", detail, ["skill", skill_name])

    def log_tool(self, tool_name: str, event: str = "enabled"):
        self.log("tool", event, f"Tool: {tool_name} {event}", "", ["tool", tool_name])

    def log_decision(self, title: str, detail: str = ""):
        self.log("decision", "decided", title, detail, ["decision"])

    def log_budget(self, event: str, detail: str = ""):
        self.log("budget", event, f"Budget: {event}", detail, ["budget"])


    def log_execution(self, title: str, detail: str = "", tags: list[str] = None):
        self.log("execution", "progressed", title, detail, tags or ["execution"])

    def log_scorecard(self, week_start: str, week_end: str, detail: str = ""):
        self.log(
            "execution",
            "scorecard",
            f"Weekly scorecard captured ({week_start} to {week_end})",
            detail,
            ["execution", "scorecard", week_start, week_end],
        )

    # ── Read ──────────────────────────────────────────────────

    def get_recent(self, limit: int = 50, category: str = None) -> list[dict]:
        """Get most recent log entries, optionally filtered by category."""
        if not self.LOG_FILE.exists():
            return []

        entries = []
        with open(self.LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if category and entry.get("category") != category:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        # Return most recent N
        return entries[-limit:]

    def get_all(self) -> list[dict]:
        """Get all log entries."""
        return self.get_recent(limit=10000)

    def get_stats(self) -> dict:
        """Summary statistics for the activity log."""
        entries = self.get_all()
        cats: dict[str, int] = {}
        for e in entries:
            cat = e.get("category", "unknown")
            cats[cat] = cats.get(cat, 0) + 1
        return {
            "total_entries": len(entries),
            "categories": cats,
            "latest": entries[-1] if entries else None,
        }

    def get_timeline(self, limit: int = 30) -> list[dict]:
        """
        Get a human-friendly timeline view — recent events with icons.
        Good for the frontend activity feed.
        """
        icons = {
            "knowledge": "📚",
            "seed": "🌱",
            "milestone": "🏆",
            "dog": "🐕",
            "decision": "⚖️",
            "reflection": "🪞",
            "skill": "⚡",
            "tool": "🔧",
            "budget": "💰",
            "execution": "🧭",
        }
        entries = self.get_recent(limit)
        timeline = []
        for e in entries:
            icon = icons.get(e.get("category", ""), "📌")
            timeline.append({
                "icon": icon,
                "title": e.get("title", ""),
                "category": e.get("category", ""),
                "event": e.get("event", ""),
                "time": e.get("timestamp", ""),
                "detail": e.get("detail", ""),
                "tags": e.get("tags", []),
            })
        return timeline
