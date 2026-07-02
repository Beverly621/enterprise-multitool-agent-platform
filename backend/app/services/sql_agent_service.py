import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun, AgentStep, AgentTrace
from app.models.audit_log import AuditLog
from app.models.sql_query import SQLQueryLog
from app.models.user import User
from app.schemas.sql_agent import SQLAgentQueryResponse
from app.services.schema_reader import read_allowed_schema
from app.services.sql_executor import execute_safe_sql
from app.services.sql_guardrails import SQLGuardrailResult, validate_sql
from app.services.sql_result_explainer import explain_sql_result


@dataclass(slots=True)
class SQLGeneration:
    sql: str
    explanation: str


def run_sql_agent(db: Session, user: User, question: str) -> SQLAgentQueryResponse:
    run_id = f"run_{uuid.uuid4().hex}"
    run = AgentRun(
        run_id=run_id,
        user_id=user.id,
        query=question,
        intent="SQL_QUERY",
        status="CREATED",
        current_step="READ_SCHEMA",
    )
    db.add(run)
    db.flush()
    _trace(db, run_id, "SQL_AGENT_STARTED", {"question": question})
    _audit(db, user.id, "SQL_AGENT_QUERY", run_id, question, None, None, 0)

    generated_sql: str | None = None
    guardrail = SQLGuardrailResult(False, None, "SQL generation did not complete.")
    rows: list[dict[str, Any]] = []
    columns: list[str] = []
    row_count = 0
    duration_ms = 0

    try:
        schema = _record_step(db, run_id, "READ_SCHEMA", {}, read_allowed_schema())
        _trace(db, run_id, "SCHEMA_READ", {"tables": [t["table_name"] for t in schema["tables"]]})

        generation = _mock_generate_sql(question)
        generated_sql = generation.sql
        _record_step(
            db,
            run_id,
            "GENERATE_SQL",
            {"question": question, "schema": schema},
            {"sql": generated_sql, "explanation": generation.explanation},
        )
        _trace(db, run_id, "SQL_GENERATED", {"sql": generated_sql})

        guardrail = validate_sql(generated_sql)
        _record_step(
            db,
            run_id,
            "SQL_GUARDRAILS",
            {"sql": generated_sql},
            {"safe": guardrail.safe, "sql": guardrail.sql, "reason": guardrail.reason},
        )

        if not guardrail.safe:
            answer = "该查询涉及危险 SQL 操作，已被系统安全策略拦截。"
            _trace(db, run_id, "SQL_BLOCKED", {"reason": guardrail.reason, "sql": generated_sql})
            _trace(db, run_id, "SQL_AGENT_FINISHED", {"status": "BLOCKED"})
            run.status = "FAILED"
            run.current_step = "SQL_GUARDRAILS"
            run.final_answer = answer
            run.error_message = guardrail.reason
            run.finished_at = datetime.now(UTC)
            _write_sql_log(
                db,
                user=user,
                run_id=run_id,
                question=question,
                generated_sql=generated_sql,
                guardrail=guardrail,
                rows=[],
                row_count=0,
                duration_ms=0,
            )
            _audit(
                db,
                user.id,
                "SQL_AGENT_BLOCKED",
                run_id,
                question,
                generated_sql,
                False,
                0,
                blocked_reason=guardrail.reason,
            )
            db.commit()
            return SQLAgentQueryResponse(
                run_id=run_id,
                question=question,
                generated_sql=generated_sql,
                safe=False,
                blocked_reason=guardrail.reason,
                answer=answer,
                trace_url=f"/api/runs/{run_id}/traces",
            )

        run.status = "QUERYING_SQL"
        run.current_step = "EXECUTE_SQL"
        execution = execute_safe_sql(db, guardrail.sql or generated_sql)
        _record_step(
            db,
            run_id,
            "EXECUTE_SQL",
            {"sql": guardrail.sql},
            {
                "columns": execution.columns,
                "row_count": execution.row_count,
                "duration_ms": execution.duration_ms,
                "error": execution.error,
            },
            status="FAILED" if execution.error else "SUCCESS",
            error_message=execution.error,
        )
        if execution.error:
            raise RuntimeError(execution.error)

        columns = execution.columns
        rows = execution.rows
        row_count = execution.row_count
        duration_ms = execution.duration_ms
        _trace(db, run_id, "SQL_EXECUTED", {"row_count": row_count, "duration_ms": duration_ms})

        answer = explain_sql_result(question, guardrail.sql or generated_sql, rows)
        _record_step(
            db,
            run_id,
            "EXPLAIN_RESULT",
            {"question": question, "sql": guardrail.sql, "rows": rows[:5]},
            {"answer": answer},
        )
        _trace(db, run_id, "SQL_EXPLAINED", {"answer": answer})

        run.status = "SUCCESS"
        run.current_step = "EXPLAIN_RESULT"
        run.final_answer = answer
        run.finished_at = datetime.now(UTC)
        _write_sql_log(
            db,
            user=user,
            run_id=run_id,
            question=question,
            generated_sql=guardrail.sql or generated_sql,
            guardrail=guardrail,
            rows=rows,
            row_count=row_count,
            duration_ms=duration_ms,
        )
        _audit(
            db,
            user.id,
            "SQL_AGENT_SUCCESS",
            run_id,
            question,
            guardrail.sql,
            True,
            duration_ms,
        )
        _trace(db, run_id, "SQL_AGENT_FINISHED", {"status": "SUCCESS"})
        db.commit()
        return SQLAgentQueryResponse(
            run_id=run_id,
            question=question,
            generated_sql=guardrail.sql,
            safe=True,
            columns=columns,
            rows=rows,
            row_count=row_count,
            duration_ms=duration_ms,
            answer=answer,
            trace_url=f"/api/runs/{run_id}/traces",
        )
    except Exception as exc:
        db.rollback()
        _mark_run_failed(db, run_id, str(exc))
        _write_sql_log(
            db,
            user=user,
            run_id=run_id,
            question=question,
            generated_sql=generated_sql,
            guardrail=guardrail,
            rows=rows,
            row_count=row_count,
            duration_ms=duration_ms,
        )
        _audit(
            db,
            user.id,
            "SQL_AGENT_FAILED",
            run_id,
            question,
            generated_sql,
            False,
            duration_ms,
            blocked_reason=str(exc),
        )
        _trace(db, run_id, "SQL_AGENT_FINISHED", {"status": "FAILED", "error": str(exc)})
        db.commit()
        return SQLAgentQueryResponse(
            run_id=run_id,
            question=question,
            generated_sql=generated_sql,
            safe=False,
            blocked_reason=str(exc),
            answer="SQL Agent 执行失败，请检查查询条件或稍后重试。",
            trace_url=f"/api/runs/{run_id}/traces",
        )


def _mock_generate_sql(question: str) -> SQLGeneration:
    q = question.lower()
    if any(word in q for word in ["删除", "delete", "drop"]):
        return SQLGeneration("DELETE FROM demo_orders;", "Dangerous query used to test guardrails.")
    if any(word in q for word in ["更新", "update"]):
        return SQLGeneration(
            "UPDATE demo_orders SET order_status = 'delivered';",
            "Dangerous update.",
        )
    if "password" in q or "users" in q:
        return SQLGeneration("SELECT password_hash FROM users LIMIT 10;", "Sensitive table test.")
    if "select *" in q:
        return SQLGeneration("SELECT * FROM demo_orders LIMIT 10;", "SELECT star test.")

    recent_filter = (
        "o.order_purchase_timestamp >= CURRENT_DATE - INTERVAL '30 days' AND "
        if "30" in q or "最近" in q
        else ""
    )
    if any(word in q for word in ["售后", "投诉", "issue", "after"]):
        return SQLGeneration(
            "SELECT a.issue_type, COUNT(*) AS issue_count "
            "FROM demo_after_sales a "
            "GROUP BY a.issue_type "
            "ORDER BY issue_count DESC LIMIT 10",
            "Group after-sales issues by issue type.",
        )
    if any(word in q for word in ["低评分", "评分", "品类", "商品", "category"]):
        return SQLGeneration(
            "SELECT p.category, COUNT(*) AS low_score_count "
            "FROM demo_reviews r "
            "JOIN demo_order_items i ON i.order_id = r.order_id "
            "JOIN demo_products p ON p.product_id = i.product_id "
            "WHERE r.review_score <= 2 "
            "GROUP BY p.category "
            "ORDER BY low_score_count DESC LIMIT 10",
            "Find categories with the most low-score orders.",
        )
    if any(word in q for word in ["延迟", "配送", "delay", "delayed"]):
        return SQLGeneration(
            "SELECT o.state, COUNT(*) AS delayed_count "
            "FROM demo_orders o "
            "WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date "
            "GROUP BY o.state "
            "ORDER BY delayed_count DESC LIMIT 10",
            "Find states with the most delayed deliveries.",
        )
    if any(word in q for word in ["地区", "state", "州", "哪里"]):
        return SQLGeneration(
            "SELECT o.state, COUNT(*) AS abnormal_count "
            "FROM demo_orders o "
            "LEFT JOIN demo_reviews r ON r.order_id = o.order_id "
            "LEFT JOIN demo_after_sales a ON a.order_id = o.order_id "
            f"WHERE {recent_filter}"
            "(o.order_status IN ('canceled', 'unavailable') "
            "OR o.order_delivered_customer_date > o.order_estimated_delivery_date "
            "OR r.review_score <= 2 OR a.issue_type IS NOT NULL) "
            "GROUP BY o.state ORDER BY abnormal_count DESC LIMIT 10",
            "Find states with the most abnormal orders.",
        )
    return SQLGeneration(
        "SELECT COUNT(DISTINCT o.order_id) AS abnormal_order_count "
        "FROM demo_orders o "
        "LEFT JOIN demo_reviews r ON r.order_id = o.order_id "
        "LEFT JOIN demo_after_sales a ON a.order_id = o.order_id "
        f"WHERE {recent_filter}"
        "(o.order_status IN ('canceled', 'unavailable') "
        "OR o.order_delivered_customer_date > o.order_estimated_delivery_date "
        "OR r.review_score <= 2 OR a.issue_type IS NOT NULL) LIMIT 100",
        "Count abnormal orders by status, delay, low score or after-sales issue.",
    )


def _record_step(
    db: Session,
    run_id: str,
    step_name: str,
    input_json: dict,
    output_json: dict,
    status: str = "SUCCESS",
    error_message: str | None = None,
) -> dict:
    now = datetime.now(UTC)
    db.add(
        AgentStep(
            run_id=run_id,
            step_name=step_name,
            step_type="SQL_AGENT",
            status=status,
            input_json=input_json,
            output_json=output_json,
            error_message=error_message,
            started_at=now,
            ended_at=now,
        )
    )
    return output_json


def _trace(db: Session, run_id: str, event_name: str, metadata: dict) -> None:
    db.add(
        AgentTrace(
            run_id=run_id,
            event_type="SQL_AGENT",
            event_name=event_name,
            content=json.dumps(metadata, ensure_ascii=False),
            metadata_json=metadata,
        )
    )


def _write_sql_log(
    db: Session,
    user: User,
    run_id: str,
    question: str,
    generated_sql: str | None,
    guardrail: SQLGuardrailResult,
    rows: list[dict[str, Any]],
    row_count: int,
    duration_ms: int,
) -> None:
    preview = rows[:5]
    db.add(
        SQLQueryLog(
            user_id=user.id,
            run_id=run_id,
            question=question,
            natural_language_query=question,
            generated_sql=generated_sql,
            safe=guardrail.safe,
            blocked_reason=guardrail.reason,
            is_allowed=guardrail.safe,
            guardrail_reason=guardrail.reason,
            result_preview=preview,
            result_json={"preview": preview},
            row_count=row_count,
            duration_ms=duration_ms,
        )
    )


def _audit(
    db: Session,
    user_id: int,
    action: str,
    run_id: str,
    question: str,
    generated_sql: str | None,
    safe: bool | None,
    duration_ms: int,
    blocked_reason: str | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=user_id,
            action=action,
            resource_type="sql_agent",
            resource_id=run_id,
            metadata_json={
                "user_id": user_id,
                "run_id": run_id,
                "question": question,
                "generated_sql": generated_sql,
                "safe": safe,
                "blocked_reason": blocked_reason,
                "duration_ms": duration_ms,
            },
        )
    )


def _mark_run_failed(db: Session, run_id: str, error_message: str) -> None:
    run = db.query(AgentRun).filter(AgentRun.run_id == run_id).one_or_none()
    if run is None:
        return
    run.status = "FAILED"
    run.error_message = error_message
    run.finished_at = datetime.now(UTC)
