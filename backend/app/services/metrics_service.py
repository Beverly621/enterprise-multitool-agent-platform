from __future__ import annotations

from collections import Counter
from datetime import datetime
from statistics import mean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun, AgentStep
from app.models.metric import EvalRun, ProviderCall
from app.models.report import Report
from app.models.sql_query import SQLQueryLog
from app.models.task_progress import FailedTask, TaskProgress
from app.models.tool import ToolCall

SUCCESS_STATUSES = {"SUCCESS", "COMPLETED", "completed", "success"}
FAILED_STATUSES = {"FAILED", "ERROR", "failed", "error"}
CANCELLED_STATUSES = {"CANCELLED", "CANCELED", "REVOKED", "cancelled", "canceled"}


def agent_run_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    runs = _scoped(db, select(AgentRun), AgentRun.user_id, user_id).scalars().all()
    durations = [_duration_ms(run.created_at, run.finished_at) for run in runs if run.finished_at]
    status_counts = Counter(run.status for run in runs)
    success = sum(status_counts[status] for status in SUCCESS_STATUSES)
    failed = sum(status_counts[status] for status in FAILED_STATUSES)
    cancelled = sum(status_counts[status] for status in CANCELLED_STATUSES)
    total = len(runs)
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "cancelled": cancelled,
        "success_rate": round(success / total, 4) if total else 0,
        "avg_duration_ms": int(mean(durations)) if durations else 0,
        "p50_duration_ms": _percentile(durations, 50),
        "p95_duration_ms": _percentile(durations, 95),
        "by_intent": dict(Counter(run.intent or "UNKNOWN" for run in runs)),
        "by_status": dict(status_counts),
        "recent_failed_runs": [_run_summary(run) for run in runs if run.status in FAILED_STATUSES][:5],
        "recent_slow_runs": [
            _run_summary(run)
            for run in sorted(runs, key=lambda item: _duration_ms(item.created_at, item.finished_at), reverse=True)[:5]
            if run.finished_at
        ],
    }


def task_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    tasks = _scoped(db, select(TaskProgress), TaskProgress.user_id, user_id).scalars().all()
    durations = [_duration_ms(task.started_at, task.finished_at) for task in tasks if task.started_at and task.finished_at]
    status_counts = Counter(task.status for task in tasks)
    failed_tasks = _scoped(db, select(FailedTask), FailedTask.user_id, user_id).scalars().all()
    failed = sum(status_counts[status] for status in FAILED_STATUSES)
    success = sum(status_counts[status] for status in SUCCESS_STATUSES)
    cancelled = sum(status_counts[status] for status in CANCELLED_STATUSES)
    timeout = status_counts.get("TIMEOUT", 0)
    total = len(tasks)
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "cancelled": cancelled,
        "timeout": timeout,
        "success_rate": round(success / total, 4) if total else 0,
        "avg_duration_ms": int(mean(durations)) if durations else 0,
        "p95_duration_ms": _percentile(durations, 95),
        "by_task_type": dict(Counter(task.task_type for task in tasks)),
        "top_errors": dict(Counter(task.error_message for task in failed_tasks if task.error_message).most_common(5)),
    }


def provider_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    calls = _scoped(db, select(ProviderCall), ProviderCall.user_id, user_id).scalars().all()
    total = len(calls)
    success = sum(1 for call in calls if call.status in SUCCESS_STATUSES)
    failed = sum(1 for call in calls if call.status in FAILED_STATUSES)
    latencies = [call.latency_ms for call in calls if call.latency_ms is not None]
    by_provider: dict[str, dict[str, Any]] = {}
    for call in calls:
        bucket = by_provider.setdefault(
            call.provider_name,
            {"calls": 0, "success": 0, "failed": 0, "cost": 0.0, "avg_latency_ms": 0},
        )
        bucket["calls"] += 1
        bucket["success"] += 1 if call.status in SUCCESS_STATUSES else 0
        bucket["failed"] += 1 if call.status in FAILED_STATUSES else 0
        bucket["cost"] += float(call.estimated_cost or 0)
    for provider, bucket in by_provider.items():
        provider_latencies = [call.latency_ms for call in calls if call.provider_name == provider]
        bucket["avg_latency_ms"] = int(mean(provider_latencies)) if provider_latencies else 0
        bucket["cost"] = round(bucket["cost"], 6)
    return {
        "total_calls": total,
        "success_calls": success,
        "failed_calls": failed,
        "success_rate": round(success / total, 4) if total else 0,
        "avg_latency_ms": int(mean(latencies)) if latencies else 0,
        "p95_latency_ms": _percentile(latencies, 95),
        "estimated_total_cost": round(sum(float(call.estimated_cost or 0) for call in calls), 6),
        "by_provider": by_provider,
        "by_request_type": dict(Counter(call.request_type for call in calls)),
    }


def rag_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    runs = _scoped(db, select(AgentRun).where(AgentRun.intent.in_(["RAG_QA", "rag"])), AgentRun.user_id, user_id).scalars().all()
    return {"queries_total": len(runs), **agent_run_metrics_for_runs(runs)}


def sql_guardrails_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    logs = _scoped(db, select(SQLQueryLog), SQLQueryLog.user_id, user_id).scalars().all()
    blocked = [log for log in logs if not log.is_allowed or log.safe is False]
    return {
        "queries_total": len(logs),
        "blocked_total": len(blocked),
        "allowed_total": len(logs) - len(blocked),
        "block_rate": round(len(blocked) / len(logs), 4) if logs else 0,
        "top_blocked_reasons": dict(Counter(log.guardrail_reason or log.blocked_reason for log in blocked).most_common(5)),
    }


def tool_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    calls = _scoped(db, select(ToolCall), ToolCall.user_id, user_id).scalars().all()
    total = len(calls)
    success = sum(1 for call in calls if call.status in SUCCESS_STATUSES)
    failed = sum(1 for call in calls if call.status in FAILED_STATUSES)
    approval_required = sum(1 for call in calls if call.requires_approval)
    latencies = [call.duration_ms for call in calls if call.duration_ms is not None]
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "tool_success_rate": round(success / total, 4) if total else 0,
        "approval_required": approval_required,
        "avg_tool_latency_ms": int(mean(latencies)) if latencies else 0,
        "by_tool": dict(Counter(call.tool_name for call in calls)),
        "failed_tool_calls": [
            {"tool_call_id": call.tool_call_id, "tool_name": call.tool_name, "error": call.error_message}
            for call in calls
            if call.status in FAILED_STATUSES
        ][:10],
    }


def summary_metrics(db: Session, user_id: int | None = None) -> dict[str, Any]:
    agent = agent_run_metrics(db, user_id)
    tasks = task_metrics(db, user_id)
    providers = provider_metrics(db, user_id)
    tools = tool_metrics(db, user_id)
    sql = sql_guardrails_metrics(db, user_id)
    reports_statement = select(func.count()).select_from(Report)
    if user_id is not None:
        reports_statement = reports_statement.where(Report.user_id == user_id)
    return {
        "agent_run_success_rate": agent["success_rate"],
        "avg_run_duration_ms": agent["avg_duration_ms"],
        "p95_run_duration_ms": agent["p95_duration_ms"],
        "rag_queries_total": rag_metrics(db, user_id)["queries_total"],
        "sql_blocked_total": sql["blocked_total"],
        "tool_success_rate": tools["tool_success_rate"],
        "async_task_success_rate": tasks["success_rate"],
        "reports_generated": int(db.scalar(reports_statement) or 0),
        "provider_calls_total": providers["total_calls"],
        "estimated_total_cost": providers["estimated_total_cost"],
        "latest_eval_runs": latest_eval_runs(db),
    }


def latest_eval_runs(db: Session) -> list[dict[str, Any]]:
    runs = db.scalars(select(EvalRun).order_by(EvalRun.id.desc()).limit(5)).all()
    return [
        {
            "eval_run_id": run.eval_run_id,
            "case_type": run.case_type,
            "status": run.status,
            "total_cases": run.total_cases,
            "pass_rate": float(run.pass_rate or 0),
            "created_at": run.created_at,
        }
        for run in runs
    ]


def agent_run_metrics_for_runs(runs: list[AgentRun]) -> dict[str, Any]:
    total = len(runs)
    success = sum(1 for run in runs if run.status in SUCCESS_STATUSES)
    failed = sum(1 for run in runs if run.status in FAILED_STATUSES)
    return {
        "success": success,
        "failed": failed,
        "success_rate": round(success / total, 4) if total else 0,
    }


def _scoped(db: Session, statement, field, user_id: int | None):
    if user_id is not None:
        statement = statement.where(field == user_id)
    return db.execute(statement)


def _duration_ms(started: datetime | None, finished: datetime | None) -> int:
    if not started or not finished:
        return 0
    return int((finished - started).total_seconds() * 1000)


def _percentile(values: list[int], percentile: int) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((percentile / 100) * (len(ordered) - 1)))
    return int(ordered[index])


def _run_summary(run: AgentRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "intent": run.intent,
        "status": run.status,
        "duration_ms": _duration_ms(run.created_at, run.finished_at),
        "error_message": run.error_message,
        "created_at": run.created_at,
    }
