from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.sql_agent_service import run_sql_agent
from app.services.tool_permission_service import highest_role_level


def run_sql_node(
    db: Session,
    run: AgentRun,
    state: AgentState,
    user: User,
    allow_user_report: bool = False,
) -> AgentState:
    started = datetime.now(UTC)
    if highest_role_level(user) < 2 and not allow_user_report:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SQL_QUERY requires Developer role or higher.",
        )
    mark_run(db, run, "QUERYING_SQL", "SQL_QUERY")
    add_trace(db, run.run_id, "SQL_NODE_STARTED", content=state["query"])
    response = run_sql_agent(db, user, state["query"])
    state["generated_sql"] = response.generated_sql
    state["sql_answer"] = response.answer
    state["sql_result"] = {
        "safe": response.safe,
        "blocked_reason": response.blocked_reason,
        "columns": response.columns,
        "rows": response.rows[:20],
        "row_count": response.row_count,
        "duration_ms": response.duration_ms,
        "sql_agent_run_id": response.run_id,
    }
    add_step(
        db,
        run.run_id,
        "SQL_QUERY",
        "sql",
        "SUCCESS" if response.safe else "FAILED",
        input_json={"query": state["query"]},
        output_json={
            "safe": response.safe,
            "generated_sql": response.generated_sql,
            "row_count": response.row_count,
            "sql_agent_run_id": response.run_id,
        },
        error_message=response.blocked_reason,
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(
        db,
        run.run_id,
        "SQL_NODE_FINISHED",
        metadata_json={"safe": response.safe, "row_count": response.row_count},
    )
    if not response.safe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=response.answer,
        )
    return state
