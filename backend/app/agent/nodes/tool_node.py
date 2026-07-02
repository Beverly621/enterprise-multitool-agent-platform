from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.tool_executor import invoke_tool, serialize_tool_call
from app.services.tool_permission_service import highest_role_level


async def run_tool_node(db: Session, run: AgentRun, state: AgentState, user: User) -> AgentState:
    started = datetime.now(UTC)
    if highest_role_level(user) < 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tool call requires User role.",
        )
    mark_run(db, run, "CALLING_TOOL", "TOOL_EXECUTION")
    tool_name, args = select_tool(state)
    state["selected_tool"] = tool_name
    state["tool_args"] = args
    add_trace(db, run.run_id, "TOOL_NODE_STARTED", metadata_json={"tool_name": tool_name})
    tool_call = await invoke_tool(
        db=db,
        user=user,
        tool_name=tool_name,
        args=args,
        run_id=run.run_id,
        session_id=state.get("session_id"),
    )
    result = serialize_tool_call(tool_call)
    state.setdefault("tool_results", []).append(result)
    if tool_call.status == "WAITING_APPROVAL":
        state["requires_approval"] = True
        if tool_call.tool_result:
            state["approval_id"] = tool_call.tool_result.get("approval_id")
    add_step(
        db,
        run.run_id,
        "TOOL_EXECUTION",
        "tool",
        tool_call.status,
        input_json={"tool_name": tool_name, "args": args},
        output_json={"tool_call_id": tool_call.tool_call_id, "status": tool_call.status},
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "TOOL_NODE_FINISHED",
        metadata_json={"tool_name": tool_name, "status": tool_call.status},
    )
    return state


def select_tool(state: AgentState) -> tuple[str, dict]:
    query = state["query"]
    slots = state.get("metadata", {}).get("intent", {}).get("slots", {})
    if state.get("intent") == "NEED_APPROVAL":
        return (
            "send_email_draft",
            {
                "to_email": slots.get("to_email", "manager@example.com"),
                "subject": "订单异常分析报告",
                "body": query,
            },
        )
    if "售后" in query and "order_" not in query.lower():
        return "query_after_sales", {"limit": 10}
    order_id = slots.get("order_id") or _extract_order_id(query)
    if order_id:
        return "query_order_status", {"order_id": order_id}
    return "create_todo", {"title": query[:120], "priority": "MEDIUM"}


def _extract_order_id(query: str) -> str | None:
    if match := re.search(r"order_[A-Za-z0-9_-]+", query, re.IGNORECASE):
        return match.group(0)
    return None
