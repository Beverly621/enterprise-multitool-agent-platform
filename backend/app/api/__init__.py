from fastapi import APIRouter

from app.api import (
    agent_chat,
    approvals,
    async_runs,
    audit,
    auth,
    chat,
    dashboard,
    documents,
    evals,
    knowledge_base,
    metrics,
    reports,
    roles,
    runs,
    sql_agent,
    tasks,
    tool_calls,
    tools,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agent_chat.router, prefix="/agent", tags=["agent"])
api_router.include_router(async_runs.router, tags=["async-runs"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, tags=["rbac"])
api_router.include_router(knowledge_base.router, prefix="/kb", tags=["knowledge-base"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(evals.router, prefix="/evals", tags=["evals"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(sql_agent.router, prefix="/sql-agent", tags=["sql-agent"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(tool_calls.router, prefix="/tool-calls", tags=["tool-calls"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, tags=["reports"])
