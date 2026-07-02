from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class IntentRoute:
    intent: str
    confidence: float
    reason: str
    slots: dict[str, Any] = field(default_factory=dict)


SUPPORTED_INTENTS = {
    "GENERAL_CHAT",
    "RAG_QA",
    "SQL_QUERY",
    "TOOL_CALL",
    "MULTI_STEP_REPORT",
    "NEED_APPROVAL",
}


def route_intent(query: str) -> IntentRoute:
    lowered = query.lower()
    normalized = query.strip()
    slots = _extract_slots(normalized)

    if any(keyword in normalized for keyword in ("发送", "邮件", "审批", "确认")):
        return IntentRoute(
            intent="NEED_APPROVAL",
            confidence=0.92,
            reason="The user asks for an operation that requires human approval.",
            slots=slots,
        )
    report_keywords = ("结合", "生成报告", "分析报告", "订单异常数据和售后知识库")
    if any(keyword in normalized for keyword in report_keywords):
        slots.setdefault("report_type", "order_abnormal_analysis")
        return IntentRoute(
            intent="MULTI_STEP_REPORT",
            confidence=0.91,
            reason="The user asks to combine business data and knowledge base context.",
            slots=slots,
        )
    tool_keywords = ("查询订单", "订单状态", "售后记录")
    if any(keyword in normalized for keyword in tool_keywords) or "order_" in lowered:
        return IntentRoute(
            intent="TOOL_CALL",
            confidence=0.88,
            reason="The user asks for a specific business tool lookup.",
            slots=slots,
        )
    sql_keywords = ("订单异常", "多少", "统计", "地区", "低评分", "售后类型", "SQL")
    if any(keyword in normalized for keyword in sql_keywords):
        return IntentRoute(
            intent="SQL_QUERY",
            confidence=0.86,
            reason="The user asks for structured business data analysis.",
            slots=slots,
        )
    rag_keywords = ("制度", "政策", "文档", "依据", "知识库", "利益冲突", "售后政策")
    if any(keyword in normalized for keyword in rag_keywords):
        return IntentRoute(
            intent="RAG_QA",
            confidence=0.84,
            reason="The user asks for knowledge-base grounded information.",
            slots=slots,
        )
    if any(keyword in normalized for keyword in ("你好", "介绍", "帮助")) or "hello" in lowered:
        return IntentRoute(
            intent="GENERAL_CHAT",
            confidence=0.8,
            reason="The user asks a general assistant question.",
            slots=slots,
        )
    return IntentRoute(
        intent="GENERAL_CHAT",
        confidence=0.55,
        reason="No specialized enterprise task was detected.",
        slots=slots,
    )


def _extract_slots(query: str) -> dict[str, Any]:
    slots: dict[str, Any] = {}
    if match := re.search(r"order_[A-Za-z0-9_-]+", query, re.IGNORECASE):
        slots["order_id"] = match.group(0)
    if match := re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", query):
        slots["to_email"] = match.group(0)
    if "最近 30 天" in query or "最近30天" in query:
        slots["time_range"] = "last_30_days"
    return slots
