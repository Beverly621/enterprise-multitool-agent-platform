# Agent Planner

阶段五实现了统一的 Agent Planner 运行时，用一个入口把普通对话、RAG、SQL Agent、Tool Calling、审批等待和多步骤报告串联起来。当前实现保持轻量 Python graph runtime，节点边界按 LangGraph 形态组织，后续可以平滑迁移到 LangGraph `StateGraph`。

## Entry Point

- API: `POST /api/agent/chat`
- Runtime: `backend/app/agent/runtime.py`
- Request: `session_id`, `query`, optional `kb_id`
- Response: `run_id`, `intent`, `status`, `answer`, optional `approval_id`, `trace_url`, citations, SQL result and tool results

The runtime creates an `agent_runs` record first, then writes one `agent_steps` row and multiple `agent_traces` rows as each node executes.

## Agent State

`backend/app/agent/state.py` defines the shared `AgentState` object. It carries:

- identity and request context: `run_id`, `user_id`, `session_id`, `query`, `kb_id`
- routing context: `intent`, `current_step`, `metadata`
- RAG output: `retrieved_chunks`, `citations`, `rag_answer`
- SQL output: `generated_sql`, `sql_result`, `sql_answer`
- tool output: `selected_tool`, `tool_args`, `tool_results`
- final output: `report`, `final_answer`
- approval and error context: `requires_approval`, `approval_id`, `error`

## Supported Intents

The intent router maps the user query into one of these planner paths:

| Intent | Flow |
| --- | --- |
| `GENERAL_CHAT` | general chat node -> final node |
| `RAG_QA` | RAG node -> final node |
| `SQL_QUERY` | SQL node -> final node |
| `TOOL_CALL` | tool node -> final node |
| `MULTI_STEP_REPORT` | SQL node -> optional RAG node -> report node -> final node |
| `NEED_APPROVAL` | tool node -> approval node -> final node |

The router is deterministic and mock-friendly so the project can run without external LLM keys. LLM-based routing can be added behind the same `route_intent` service contract.

## Node Responsibilities

- `intent_router`: classifies query intent, records routing metadata and updates run status.
- `general_chat_node`: returns a concise platform-aware assistant answer for non-tool questions.
- `rag_node`: reuses `rag_service.semantic_search` and knowledge-base access checks, then produces an answer with citations.
- `sql_node`: reuses `sql_agent_service.run_sql_agent`; SQL generation and execution still pass through SQL Guardrails.
- `tool_node`: selects a registered tool, invokes `tool_executor.invoke_tool`, validates RBAC and captures approval state.
- `approval_node`: marks the run as `WAITING_APPROVAL` when a tool creates an approval request.
- `report_node`: combines SQL findings and optional RAG evidence into a structured Chinese report.
- `final_node`: stores the final answer, closes the run, and writes success or waiting traces.

## Status Model

The planner uses explicit statuses so the workflow is visible in the database and API:

- `CREATED`
- `ROUTING`
- `RETRIEVING`
- `QUERYING_SQL`
- `CALLING_TOOL`
- `GENERATING_REPORT`
- `WAITING_APPROVAL`
- `FINALIZING`
- `SUCCESS`
- `FAILED`
- `CANCELLED`

## Trace Events

Important events are written to `agent_traces`:

- `AGENT_RUN_CREATED`
- `INTENT_ROUTER_STARTED`
- `INTENT_ROUTER_FINISHED`
- `RAG_NODE_STARTED`
- `RAG_NODE_FINISHED`
- `SQL_NODE_STARTED`
- `SQL_NODE_FINISHED`
- `TOOL_NODE_STARTED`
- `TOOL_NODE_FINISHED`
- `REPORT_NODE_STARTED`
- `REPORT_NODE_FINISHED`
- `APPROVAL_REQUIRED`
- `FINAL_NODE_STARTED`
- `FINAL_NODE_FINISHED`
- `AGENT_RUN_SUCCESS`
- `AGENT_RUN_FAILED`

Trace payloads are sanitized before persistence to avoid logging passwords, tokens, API keys or long raw payloads.

## RBAC

Planner-level RBAC is enforced before executing the chosen path:

- Guest: general chat and accessible/public RAG only.
- User: general chat, RAG, normal tools and controlled multi-step reports.
- Developer: SQL Agent plus User permissions.
- Admin: all planner paths and all run visibility.

Tool-level permissions are still checked by `tool_executor`, and SQL tools still use the safe SQL execution path.

## Run APIs

- `GET /api/runs`: list visible runs. Admin and trace readers can see all runs; normal users see their own.
- `GET /api/runs/{run_id}`: read run summary.
- `GET /api/runs/{run_id}/steps`: read ordered planner steps.
- `GET /api/runs/{run_id}/tool-calls`: read tool calls attached to a run.
- `GET /api/runs/{run_id}/traces`: read ordered trace events.

## Multi-Step Report Format

`MULTI_STEP_REPORT` renders Markdown with the required sections:

```markdown
# 业务分析报告

## 一、数据来源
## 二、核心发现
## 三、异常原因分析
## 四、知识库依据
## 五、改进建议
## 六、引用来源
## 七、生成时间
```

The report path reuses SQL Agent output as structured business data and optional RAG citations as policy evidence.

## Local Verification

Stage five adds focused tests:

- `test_agent_intent_router.py`
- `test_agent_runtime.py`
- `test_agent_chat_api.py`
- `test_agent_multistep_report.py`
- `test_agent_trace.py`

Run all backend tests with:

```bash
PYTHONPATH=backend python3 -m pytest backend/app/tests
```
