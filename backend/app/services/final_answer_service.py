from app.agent.state import AgentState


def build_final_answer(state: AgentState) -> str:
    if state.get("requires_approval"):
        approval_id = state.get("approval_id")
        return f"该操作需要人工审批，请确认后继续。approval_id={approval_id}"
    if state.get("report"):
        return str(state["report"])
    if state.get("rag_answer"):
        return str(state["rag_answer"])
    if state.get("sql_answer"):
        return str(state["sql_answer"])
    if state.get("tool_results"):
        return f"工具调用完成：{state['tool_results'][-1]}"
    return str(state.get("final_answer") or "任务已完成。")
