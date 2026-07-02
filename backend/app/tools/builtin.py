from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.models.demo_order import DemoAfterSales, DemoOrder, DemoReview
from app.models.sql_query import SQLQueryLog
from app.models.tool import Todo
from app.services.rag_service import semantic_search
from app.services.report_service import render_business_report
from app.services.sql_executor import execute_safe_sql
from app.services.sql_guardrails import validate_sql
from app.tools.base import ToolContext, ToolMetadata


def _object_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


class SearchKnowledgeBaseTool:
    metadata = ToolMetadata(
        name="search_knowledge_base",
        description="Search an enterprise knowledge base through the RAG vector pipeline.",
        schema_json=_object_schema(
            {
                "kb_id": {"type": "integer", "minimum": 1},
                "query": {"type": "string", "minLength": 1},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                "metadata_filter": {"type": "object"},
            },
            ["kb_id", "query"],
        ),
        permission_level="Guest",
        require_approval=False,
        timeout_ms=8000,
        retry_count=1,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        result = semantic_search(
            context.db,
            kb_id=int(args["kb_id"]),
            query=str(args["query"]),
            top_k=int(args.get("top_k", 5)),
            metadata_filter=args.get("metadata_filter"),
        )
        return result.model_dump()


class ExecuteSafeSQLTool:
    metadata = ToolMetadata(
        name="execute_safe_sql",
        description="Run SQL through SQL Guardrails and a read-only executor.",
        schema_json=_object_schema(
            {
                "sql": {"type": "string", "minLength": 1},
                "question": {"type": "string"},
                "max_rows": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            ["sql"],
        ),
        permission_level="Developer",
        require_approval=False,
        timeout_ms=10000,
        retry_count=0,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        sql = str(args["sql"])
        guardrail = validate_sql(sql)
        if not guardrail.safe:
            _write_sql_log(context, args, guardrail.safe, guardrail.reason, sql, [], 0, 0)
            return {
                "safe": False,
                "blocked_reason": guardrail.reason,
                "rows": [],
                "row_count": 0,
            }

        execution = execute_safe_sql(
            context.db,
            guardrail.sql or sql,
            max_rows=int(args.get("max_rows", 100)),
        )
        _write_sql_log(
            context,
            args,
            execution.error is None,
            execution.error,
            guardrail.sql or sql,
            execution.rows,
            execution.row_count,
            execution.duration_ms,
        )
        if execution.error:
            raise RuntimeError(execution.error)
        return {
            "safe": True,
            "columns": execution.columns,
            "rows": execution.rows,
            "row_count": execution.row_count,
            "duration_ms": execution.duration_ms,
        }


class QueryOrderStatusTool:
    metadata = ToolMetadata(
        name="query_order_status",
        description="Query demo order status, delivery delay, review and after-sales summary.",
        schema_json=_object_schema(
            {"order_id": {"type": "string", "minLength": 1}},
            ["order_id"],
        ),
        permission_level="User",
        require_approval=False,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        order_id = str(args["order_id"])
        order = context.db.scalar(select(DemoOrder).where(DemoOrder.order_id == order_id))
        if order is None:
            return {"found": False, "order_id": order_id}
        review = context.db.scalar(select(DemoReview).where(DemoReview.order_id == order_id))
        cases = context.db.scalars(
            select(DemoAfterSales).where(DemoAfterSales.order_id == order_id)
        ).all()
        delay_days = None
        if order.order_delivered_customer_date and order.order_estimated_delivery_date:
            delay_days = (
                order.order_delivered_customer_date - order.order_estimated_delivery_date
            ).days
        return {
            "found": True,
            "order_id": order.order_id,
            "status": order.order_status,
            "payment_value": order.payment_value,
            "state": order.state,
            "estimated_delivery": _iso(order.order_estimated_delivery_date),
            "delivered_at": _iso(order.order_delivered_customer_date),
            "delay_days": delay_days,
            "review_score": review.review_score if review else None,
            "after_sales": [
                {
                    "after_sales_id": item.after_sales_id,
                    "issue_type": item.issue_type,
                    "status": item.status,
                    "description": item.issue_description,
                }
                for item in cases
            ],
        }


class QueryAfterSalesTool:
    metadata = ToolMetadata(
        name="query_after_sales",
        description="Query demo after-sales cases by order id or issue type.",
        schema_json=_object_schema(
            {
                "order_id": {"type": "string"},
                "issue_type": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
        ),
        permission_level="User",
        require_approval=False,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        statement = select(DemoAfterSales)
        if args.get("order_id"):
            statement = statement.where(DemoAfterSales.order_id == str(args["order_id"]))
        if args.get("issue_type"):
            statement = statement.where(DemoAfterSales.issue_type == str(args["issue_type"]))
        cases = context.db.scalars(statement.limit(int(args.get("limit", 10)))).all()
        return {
            "count": len(cases),
            "cases": [
                {
                    "after_sales_id": item.after_sales_id,
                    "order_id": item.order_id,
                    "issue_type": item.issue_type,
                    "status": item.status,
                    "description": item.issue_description,
                    "created_at": _iso(item.created_at),
                }
                for item in cases
            ],
        }


class GenerateReportTool:
    metadata = ToolMetadata(
        name="generate_report",
        description="Generate a structured Markdown business report from provided findings.",
        schema_json=_object_schema(
            {
                "title": {"type": "string", "minLength": 1},
                "data_sources": {"type": "array", "items": {"type": "string"}},
                "findings": {"type": "array", "items": {"type": "string"}},
                "analysis": {"type": "string"},
                "knowledge_basis": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}},
            },
            ["title"],
        ),
        permission_level="User",
        require_approval=False,
        timeout_ms=5000,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        content = render_business_report(
            title=str(args["title"]),
            data_sources=args.get("data_sources", []),
            findings=args.get("findings", []),
            analysis=args.get("analysis"),
            knowledge_basis=args.get("knowledge_basis", []),
            recommendations=args.get("recommendations", []),
        )
        return {"format": "markdown", "content": content}


class SendEmailDraftTool:
    metadata = ToolMetadata(
        name="send_email_draft",
        description="Create an email draft that must be approved before any outbound action.",
        schema_json=_object_schema(
            {
                "to_email": {"type": "string", "format": "email"},
                "subject": {"type": "string", "minLength": 1},
                "body": {"type": "string", "minLength": 1},
            },
            ["to_email", "subject", "body"],
        ),
        permission_level="User",
        require_approval=True,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        return {
            "status": "WAITING_APPROVAL",
            "message": "Email drafts are prepared by ToolExecutor before approval.",
        }


class CreateTodoTool:
    metadata = ToolMetadata(
        name="create_todo",
        description="Create a follow-up todo item for the current user.",
        schema_json=_object_schema(
            {
                "title": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
            },
            ["title"],
        ),
        permission_level="User",
        require_approval=False,
    )

    async def execute(self, args: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        todo = Todo(
            todo_id=f"todo_{uuid.uuid4().hex}",
            user_id=context.user.id,
            title=str(args["title"]),
            description=args.get("description"),
            priority=str(args.get("priority", "MEDIUM")),
            source_run_id=context.run_id,
        )
        context.db.add(todo)
        context.db.flush()
        return {
            "todo_id": todo.todo_id,
            "title": todo.title,
            "status": todo.status,
            "priority": todo.priority,
        }


def get_builtin_tools() -> dict[str, Any]:
    tools = [
        SearchKnowledgeBaseTool(),
        ExecuteSafeSQLTool(),
        QueryOrderStatusTool(),
        QueryAfterSalesTool(),
        GenerateReportTool(),
        SendEmailDraftTool(),
        CreateTodoTool(),
    ]
    return {tool.metadata.name: tool for tool in tools}


def _write_sql_log(
    context: ToolContext,
    args: dict[str, Any],
    safe: bool,
    blocked_reason: str | None,
    sql: str,
    rows: list[dict[str, Any]],
    row_count: int,
    duration_ms: int,
) -> None:
    question = args.get("question") or f"Tool SQL: {sql[:120]}"
    context.db.add(
        SQLQueryLog(
            user_id=context.user.id,
            run_id=context.run_id,
            question=question,
            natural_language_query=question,
            generated_sql=sql,
            safe=safe,
            blocked_reason=blocked_reason,
            is_allowed=safe,
            guardrail_reason=blocked_reason,
            result_preview=rows[:5],
            result_json={"rows": rows[:20]},
            row_count=row_count,
            duration_ms=duration_ms,
        )
    )


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
