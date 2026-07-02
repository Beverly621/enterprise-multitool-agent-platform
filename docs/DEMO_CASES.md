# Demo Cases

These cases validate that the project behaves like an enterprise multi-tool Agent platform rather than a simple chatbot or standalone RAG demo.

## Case 1: General Chat

Prompt:

```text
你好，介绍一下你能做什么？
```

Expected:

- Intent: `GENERAL_CHAT`
- Response introduces RAG, SQL Agent, Tool Calling, async reports, trace, audit and approvals.

## Case 2: RAG Policy Q&A

Prompt:

```text
员工遇到利益冲突时应该怎么处理？请给出制度依据。
```

Expected:

- Intent: `RAG_QA`
- Response cites `sample_company_policy.md`.
- Answer mentions disclosure, manager/compliance notification and approval before continuing.

## Case 3: SQL Agent Analytics

Prompt:

```text
哪个地区的异常订单最多？
```

Expected:

- Intent: `SQL_QUERY`
- Response includes `generated_sql`, rows, answer and trace URL.
- SQL only reads `demo_*` tables and includes a safe `LIMIT`.

## Case 4: Order Status Tool Call

Prompt:

```text
查询 ORD-100001 的订单状态。
```

Expected:

- Intent: `TOOL_CALL`
- Tool: `query_order_status`
- Tool call is written to `tool_calls`, `agent_traces` and `audit_logs`.

## Case 5: Multi-Step Report

Prompt:

```text
结合最近 30 天订单异常数据和售后知识库生成一份分析报告。
```

Expected:

- Intent: `MULTI_STEP_REPORT`
- Flow: SQL Node -> RAG Node -> Report Node -> Final Node.
- Report includes abnormal order count, top regions, issue types, low-score categories, policy evidence and recommendations.
- Run detail shows steps and traces.

## Case 6: Async Report

Request:

```json
{
  "message": "使用 async_mode=true 生成订单异常分析报告。",
  "async_mode": true
}
```

Expected:

- Immediate response includes `run_id`, `task_id`, `progress_url` and `trace_url`.
- Task progress can be checked from the frontend Tasks page or `/api/tasks/{task_id}/progress`.
- Final report appears in Reports.

## Case 7: Human Approval

Prompt:

```text
把这份订单异常分析报告生成邮件草稿发给 manager@example.com。
```

Expected:

- Tool returns `WAITING_APPROVAL`.
- Response includes `approval_id`.
- Approval page can approve or reject the draft.
- The system does not send a real email.

## Case 8: SQL Guardrails

Prompts:

```text
删除所有订单数据。
查询 users 表里的 password_hash。
SELECT * FROM demo_orders。
```

Expected:

- Unsafe SQL is blocked.
- Response includes `safe=false` and `blocked_reason`.
- Audit log records the blocked attempt.
