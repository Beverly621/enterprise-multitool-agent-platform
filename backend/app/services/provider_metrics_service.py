from __future__ import annotations

import re
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
from typing import Iterator

from sqlalchemy.orm import Session

from app.models.metric import ProviderCall

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|authorization|token|secret|password)\s*[:=]\s*(?:Bearer\s+)?[^,\s]+"),
]


@dataclass(frozen=True, slots=True)
class ProviderMetricsContext:
    db: Session | None = None
    run_id: str | None = None
    step_id: int | None = None
    user_id: int | None = None
    request_type: str = "LLM_CHAT"


_provider_context: ContextVar[ProviderMetricsContext | None] = ContextVar(
    "provider_metrics_context",
    default=None,
)


@contextmanager
def provider_metrics_scope(
    db: Session | None = None,
    run_id: str | None = None,
    step_id: int | None = None,
    user_id: int | None = None,
    request_type: str | None = None,
) -> Iterator[None]:
    previous = _provider_context.get()
    merged = ProviderMetricsContext(
        db=db if db is not None else (previous.db if previous else None),
        run_id=run_id if run_id is not None else (previous.run_id if previous else None),
        step_id=step_id if step_id is not None else (previous.step_id if previous else None),
        user_id=user_id if user_id is not None else (previous.user_id if previous else None),
        request_type=request_type or (previous.request_type if previous else "LLM_CHAT"),
    )
    token = _provider_context.set(merged)
    try:
        yield
    finally:
        _provider_context.reset(token)


@contextmanager
def provider_request_type(request_type: str) -> Iterator[None]:
    current = _provider_context.get() or ProviderMetricsContext()
    token = _provider_context.set(replace(current, request_type=request_type))
    try:
        yield
    finally:
        _provider_context.reset(token)


def record_provider_call(
    provider_name: str,
    model_name: str | None,
    request_type: str,
    status: str,
    latency_ms: int,
    input_text: str = "",
    output_text: str = "",
    error: Exception | str | None = None,
) -> None:
    context = _provider_context.get()
    if context is None or context.db is None:
        return
    error_message = _sanitize_error(error)
    context.db.add(
        ProviderCall(
            call_id=f"pc_{uuid.uuid4().hex}",
            run_id=context.run_id,
            step_id=context.step_id,
            user_id=context.user_id,
            provider_name=provider_name,
            model_name=model_name,
            request_type=request_type,
            status=status,
            latency_ms=max(latency_ms, 0),
            input_tokens=_estimate_tokens(input_text),
            output_tokens=_estimate_tokens(output_text),
            estimated_cost=_estimate_cost(provider_name, input_text, output_text),
            error_type=error.__class__.__name__ if isinstance(error, Exception) else None,
            error_message=error_message,
        )
    )


def time_provider_call(
    provider_name: str,
    model_name: str | None,
    input_text: str,
    output_text: str = "",
    error: Exception | str | None = None,
    status: str = "SUCCESS",
    started: float | None = None,
    request_type: str | None = None,
) -> None:
    started_at = started if started is not None else time.perf_counter()
    context = _provider_context.get()
    record_provider_call(
        provider_name=provider_name,
        model_name=model_name,
        request_type=request_type or (context.request_type if context else "LLM_CHAT"),
        status=status,
        latency_ms=int((time.perf_counter() - started_at) * 1000),
        input_text=input_text,
        output_text=output_text,
        error=error,
    )


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def _estimate_cost(provider_name: str, input_text: str, output_text: str) -> float:
    if provider_name.lower() == "mock":
        return 0.0
    input_tokens = _estimate_tokens(input_text)
    output_tokens = _estimate_tokens(output_text)
    return round(input_tokens * 0.00000015 + output_tokens * 0.0000006, 6)


def _sanitize_error(error: Exception | str | None) -> str | None:
    if error is None:
        return None
    message = str(error)
    for pattern in SECRET_PATTERNS:
        message = pattern.sub("[REDACTED]", message)
    return message[:1000]
