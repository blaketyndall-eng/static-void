"""Sprint 12: local artifact registry for governance outputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class ArtifactRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def register(self, artifact_type: str, payload: dict) -> Path:
        ts = datetime.now(timezone.utc).isoformat().replace(":", "-")[:19]
        path = self.root / f"{artifact_type}_{ts}.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def list_artifacts(self, artifact_type: str | None = None) -> list[Path]:
        files = sorted(self.root.glob("*.json"))
        if artifact_type:
            files = [f for f in files if f.name.startswith(f"{artifact_type}_")]
        return files

    def latest(self, artifact_type: str | None = None) -> Path | None:
        files = self.list_artifacts(artifact_type=artifact_type)
        return files[-1] if files else None
