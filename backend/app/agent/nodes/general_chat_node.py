from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.provider_base import ChatMessage
from app.services.provider_factory import get_llm_provider


def run_general_chat_node(db: Session, run: AgentRun, state: AgentState) -> AgentState:
    started = datetime.now(UTC)
    mark_run(db, run, "FINALIZING", "GENERAL_CHAT")
    add_trace(db, run.run_id, "GENERAL_CHAT_STARTED", content=state["query"])
    answer = get_llm_provider().chat(
        [
            ChatMessage(
                role="system",
                content=(
                    "You are an enterprise AI agent platform assistant. "
                    "Briefly introduce RAG, SQL Agent, Tool Calling and reports."
                ),
            ),
            ChatMessage(role="user", content=state["query"]),
        ]
    )
    if answer.startswith("[MockLLM]"):
        answer = (
            "你好，我是企业级多工具 Agent。"
            "我可以做知识库问答、结构化数据查询、工具调用、审批流和多步骤报告生成。"
        )
    state["final_answer"] = answer
    add_step(
        db,
        run.run_id,
        "GENERAL_CHAT",
        "llm",
        "SUCCESS",
        input_json={"query": state["query"]},
        output_json={"answer": answer},
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(db, run.run_id, "GENERAL_CHAT_FINISHED", metadata_json={"answer_chars": len(answer)})
    return state
