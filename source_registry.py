from domain_models import SourceRecord, SourceType, new_id


class SourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}

    def create(
        self,
        *,
        name: str,
        source_type: SourceType,
        trust_score: float = 0.5,
        freshness_label: str = "unknown",
        owner: str | None = None,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> SourceRecord:
        source = SourceRecord(
            id=new_id("src"),
            name=name,
            source_type=source_type,
            trust_score=trust_score,
            freshness_label=freshness_label,
            owner=owner,
            notes=notes,
            tags=tags or [],
        )
        self._sources[source.id] = source
        return source

    def list(self) -> list[SourceRecord]:
        return list(self._sources.values())

    def get(self, source_id: str) -> SourceRecord | None:
        return self._sources.get(source_id)
