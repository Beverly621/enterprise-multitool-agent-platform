from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun, AgentStep, AgentTrace

SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


def mark_run(db: Session, run: AgentRun, status: str, current_step: str) -> None:
    run.status = status
    run.current_step = current_step
    run.updated_at = datetime.now(UTC)
    db.flush()


def add_step(
    db: Session,
    run_id: str,
    step_name: str,
    step_type: str,
    status: str,
    input_json: dict[str, Any] | None = None,
    output_json: dict[str, Any] | None = None,
    error_message: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
) -> AgentStep:
    step = AgentStep(
        run_id=run_id,
        step_name=step_name,
        step_type=step_type,
        status=status,
        input_json=sanitize_payload(input_json),
        output_json=sanitize_payload(output_json),
        error_message=error_message,
        started_at=started_at or datetime.now(UTC),
        ended_at=ended_at or datetime.now(UTC),
    )
    db.add(step)
    db.flush()
    return step


def add_trace(
    db: Session,
    run_id: str,
    event_name: str,
    event_type: str = "agent",
    content: str | None = None,
    metadata_json: dict[str, Any] | None = None,
    duration_ms: int | None = None,
) -> AgentTrace:
    trace = AgentTrace(
        run_id=run_id,
        event_type=event_type,
        event_name=event_name,
        content=content,
        metadata_json=sanitize_payload(metadata_json),
        duration_ms=duration_ms,
    )
    db.add(trace)
    db.flush()
    return trace


def sanitize_payload(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "***"
            else:
                sanitized[key] = sanitize_payload(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value[:20]]
    if isinstance(value, str) and len(value) > 2000:
        return value[:2000] + "...[truncated]"
    return value
