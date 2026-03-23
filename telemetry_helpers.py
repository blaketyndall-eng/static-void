from typing import Any

from telemetry_logger import TelemetryLogger


def emit_view_event(logger: TelemetryLogger, event_name: str, **payload: Any) -> dict[str, Any]:
    return logger.emit(event_name, payload)


def emit_action_event(logger: TelemetryLogger, event_name: str, **payload: Any) -> dict[str, Any]:
    return logger.emit(event_name, payload)


def emit_failure_event(
    logger: TelemetryLogger,
    event_name: str,
    *,
    reason: str,
    **payload: Any,
) -> dict[str, Any]:
    return logger.emit(event_name, {"reason": reason, **payload})
