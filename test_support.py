from pathlib import Path
from typing import Iterable

import db_session
from db_models_sqlalchemy import Base as CoreBase
from decision_outputs_db_models import ArtifactORM, EvidenceORM, RecommendationORM


DEFAULT_TELEMETRY_PATHS = [
    "var/backend_packaged_telemetry.jsonl",
    "var/product_surface_packaged_telemetry.jsonl",
    "var/decision_board_telemetry.jsonl",
    "var/evaluation_surface_telemetry.jsonl",
    "var/activity_surface_telemetry.jsonl",
    "var/recommendation_telemetry.jsonl",
]


def reset_database_state(extra_paths: Iterable[str] | None = None) -> None:
    db_path = Path("decision_intelligence.db")
    if db_path.exists():
        db_path.unlink()

    paths = list(DEFAULT_TELEMETRY_PATHS)
    if extra_paths:
        paths.extend(extra_paths)

    for item in paths:
        path = Path(item)
        if path.exists():
            path.unlink()

    CoreBase.metadata.create_all(bind=db_session.engine)
    ArtifactORM.metadata.create_all(bind=db_session.engine)
    RecommendationORM.metadata.create_all(bind=db_session.engine)
    EvidenceORM.metadata.create_all(bind=db_session.engine)
