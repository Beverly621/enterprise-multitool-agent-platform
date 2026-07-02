from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.state import AgentState
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.agent_step_service import add_step, add_trace, mark_run
from app.services.report_service import render_report


def run_report_node(db: Session, run: AgentRun, state: AgentState, user: User) -> AgentState:
    started = datetime.now(UTC)
    mark_run(db, run, "GENERATING_REPORT", "REPORT_GENERATION")
    add_trace(db, run.run_id, "REPORT_NODE_STARTED")
    sql_result = state.get("sql_result") or {}
    citations = state.get("citations") or []
    retrieved = state.get("retrieved_chunks") or []
    sections = [
        "## 一、数据来源\n- demo_orders / demo_reviews / demo_after_sales\n- knowledge base",
        (
            f"## 二、核心发现\n- SQL row_count: {sql_result.get('row_count', 0)}\n"
            f"- {state.get('sql_answer') or '暂无 SQL 结论。'}"
        ),
        "## 三、异常原因分析\n- 配送延迟、低评分和售后问题需要持续复盘。",
        f"## 四、知识库依据\n{_render_knowledge_basis(retrieved)}",
        "## 五、改进建议\n- 优化物流预警。\n- 提升售后响应速度。\n- 对低评分订单进行专项复盘。",
        f"## 六、引用来源\n{_render_citations(citations)}",
        f"## 七、生成时间\n{datetime.now(UTC).isoformat()}",
    ]
    report = render_report("最近 30 天订单异常分析报告", sections)
    state["report"] = report
    add_step(
        db,
        run.run_id,
        "REPORT_GENERATION",
        "report",
        "SUCCESS",
        input_json={"sql_result": sql_result, "citation_count": len(citations)},
        output_json={"report_chars": len(report)},
        started_at=started,
        ended_at=datetime.now(UTC),
    )
    add_trace(db, run.run_id, "REPORT_NODE_FINISHED", metadata_json={"report_chars": len(report)})
    return state


def _render_knowledge_basis(chunks: list[dict]) -> str:
    if not chunks:
        return "- 未检索到知识库内容。"
    return "\n".join(
        f"- {chunk.get('filename')}#{chunk.get('chunk_index')}" for chunk in chunks[:5]
    )


def _render_citations(citations: list[dict]) -> str:
    if not citations:
        return "- 无引用。"
    return "\n".join(
        f"- document_id={item.get('document_id')}, chunk_index={item.get('chunk_index')}"
        for item in citations[:5]
    )
