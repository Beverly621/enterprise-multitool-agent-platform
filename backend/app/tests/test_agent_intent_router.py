from app.services.intent_router_service import route_intent


def test_intent_router_general_chat() -> None:
    assert route_intent("你好，介绍一下你能做什么？").intent == "GENERAL_CHAT"


def test_intent_router_rag_qa() -> None:
    assert route_intent("员工遇到利益冲突时应该怎么处理？请给出制度依据。").intent == "RAG_QA"


def test_intent_router_sql_query() -> None:
    assert route_intent("哪个地区的订单异常最多？").intent == "SQL_QUERY"


def test_intent_router_tool_call() -> None:
    route = route_intent("查询 order_001 的订单状态。")

    assert route.intent == "TOOL_CALL"
    assert route.slots["order_id"] == "order_001"


def test_intent_router_multi_step_report() -> None:
    route = route_intent("结合最近 30 天订单异常数据和售后知识库生成一份分析报告。")

    assert route.intent == "MULTI_STEP_REPORT"
    assert route.slots["time_range"] == "last_30_days"


def test_intent_router_need_approval() -> None:
    route = route_intent("把这份报告生成邮件草稿发给 manager@example.com，需要审批。")

    assert route.intent == "NEED_APPROVAL"
    assert route.slots["to_email"] == "manager@example.com"
