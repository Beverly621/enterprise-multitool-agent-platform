from typing import Any

from app.services.provider_base import ChatMessage
from app.services.provider_factory import get_llm_provider


def explain_sql_result(question: str, sql: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "本次查询没有返回结果。建议扩大时间范围或检查是否存在对应业务数据。"

    top_row = rows[0]
    top_label = _first_dimension_value(top_row)
    top_count = _first_numeric_value(top_row)
    template = (
        f"根据查询结果，核心发现集中在 {top_label}，数量为 {top_count}。"
        "建议进一步结合售后记录、低评分评论和配送延迟维度分析具体原因。"
    )

    provider = get_llm_provider()
    if provider.name == "mock":
        return template

    return provider.chat(
        [
            ChatMessage(
                role="system",
                content="Explain SQL results for a business user in Chinese.",
            ),
            ChatMessage(
                role="user",
                content=f"Question: {question}\nSQL: {sql}\nRows: {rows[:5]}\nExplain findings.",
            ),
        ]
    )


def _first_dimension_value(row: dict[str, Any]) -> str:
    for value in row.values():
        if isinstance(value, str):
            return value
    return "当前结果"


def _first_numeric_value(row: dict[str, Any]) -> Any:
    for value in row.values():
        if isinstance(value, int | float):
            return value
    return "N/A"
