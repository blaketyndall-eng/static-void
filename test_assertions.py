from telemetry_logger import TelemetryLogger


def assert_telemetry_contains(filepath: str, expected_event_names: list[str], *, limit: int = 50) -> None:
    telemetry = TelemetryLogger(filepath=filepath)
    events = telemetry.recent(limit=limit)
    names = [row.get("event_name") for row in events]
    for expected in expected_event_names:
        assert expected in names, f"missing telemetry event: {expected}; saw {names}"


def assert_counts(payload: dict, **expected_counts: int) -> None:
    counts = payload.get("counts", {})
    for key, expected in expected_counts.items():
        assert counts.get(key) == expected, f"expected counts[{key}]={expected}, saw {counts.get(key)}"
