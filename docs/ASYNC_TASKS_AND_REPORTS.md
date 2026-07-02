# Async Tasks And Reports

阶段六在 Agent Planner 之上增加异步任务工程层。它不重写阶段五的路由和节点，而是让长时间运行的 Agent Run、报告生成和后续后台流程可以通过 Celery 执行，并通过数据库记录进度、失败、幂等和报告历史。

## Stage Goal

- `POST /api/agent/chat` 支持 `async_mode=true`。
- 异步请求立即返回 `run_id` 和 `task_id`。
- Worker 后台执行已有 Agent Runtime。
- 用户可以查询进度、取消任务、查看报告历史。
- 失败任务进入轻量 Dead Letter 表。
- 多步骤报告保存为 Markdown，后续可扩展导出 PDF、DOCX 或 HTML。

## Async Agent Run

同步模式保持阶段五行为：

```json
{
  "query": "介绍一下平台能力",
  "async_mode": false
}
```

异步模式创建 `agent_runs`、`task_progress` 和可选 `idempotency_keys` 后立即返回：

```json
{
  "session_id": "session_demo_001",
  "query": "结合最近 30 天订单异常数据和售后知识库生成一份分析报告",
  "kb_id": 1,
  "async_mode": true,
  "idempotency_key": "demo-report-001"
}
```

响应：

```json
{
  "run_id": "run_xxx",
  "task_id": "task_xxx",
  "status": "PENDING",
  "message": "Agent task has been submitted.",
  "progress_url": "/api/runs/run_xxx/progress",
  "trace_url": "/api/runs/run_xxx/traces"
}
```

## Celery Tasks

- `agent.run_async`: 执行已有 Agent Runtime，并复用同一条 `agent_runs`。
- `reports.generate_async`: 单独后台生成 Markdown 报告并保存历史。
- `tasks.cleanup_expired`: 预留清理任务入口。
- `tasks.retry_failed`: 预留失败任务人工重试入口。

Celery 配置显式导入所有任务模块，Backend 和 Worker 都使用 `app.core.config.settings`，因此 Mock Provider 下无需真实 API Key 即可启动。

## Tables

### task_progress

记录异步任务进度：

- `task_id`
- `run_id`
- `user_id`
- `task_type`
- `status`
- `progress`
- `current_stage`
- `message`
- `error_message`
- `started_at`
- `updated_at`
- `finished_at`

状态包括 `PENDING`、`RUNNING`、`WAITING_APPROVAL`、`RETRYING`、`SUCCESS`、`FAILED`、`CANCELLED` 和 `TIMEOUT`。

### failed_tasks

失败任务 Dead Letter：

- `task_id`
- `run_id`
- `user_id`
- `task_type`
- `error_message`
- `error_detail`
- `retry_count`
- `max_retry_count`
- `last_retry_at`
- `status`

写入时同步记录 `TASK_FAILED` trace 和 `TASK_FAILED_RECORDED` audit。

### idempotency_keys

防止重复提交：

- 同一 `user_id + idempotency_key + request_hash` 返回已有 `run_id/task_id`。
- 同 key 不同请求返回 `409 Conflict`。
- key 默认 24 小时过期。

### reports

保存报告历史：

- `report_id`
- `run_id`
- `user_id`
- `title`
- `report_type`
- `content_markdown`
- `summary`
- `source_metadata_json`
- `status`

报告内容保存 Markdown，source metadata 会经过敏感字段清理。

## Progress Templates

通用异步任务：

```text
0%   CREATED
10%  ROUTING
25%  SQL_QUERY
45%  RAG_RETRIEVAL
65%  TOOL_CALL
80%  REPORT_GENERATION
95%  FINALIZING / WAITING_APPROVAL
100% SUCCESS
```

当前实现以任务级进度为主，Agent 节点级步骤仍写入 `agent_steps` 和 `agent_traces`。后续可以在每个节点开始时继续细化进度更新。

## Cancellation

API：

- `POST /api/runs/{run_id}/cancel`
- `POST /api/tasks/{task_id}/cancel`

取消逻辑：

- 用户只能取消自己的任务，Admin 可以取消全部任务。
- `SUCCESS`、`FAILED`、`CANCELLED`、`TIMEOUT` 不可再次取消。
- 取消后更新 `task_progress.status = CANCELLED`。
- 同步更新 `agent_runs.status = CANCELLED`。
- 写入 `TASK_CANCEL_REQUESTED`、`TASK_CANCELLED` trace 和 `ASYNC_AGENT_RUN_CANCELLED` audit。

Worker 在任务开始前和 Agent Runtime 返回后检查取消状态。更细粒度的节点间取消检查可以在后续阶段继续增强。

## Retry Strategy

Celery 任务配置：

```text
max_retries = 2
retry_backoff = true
retry_jitter = true
```

临时异常可重试；权限不足、Guardrails 拦截、资源不存在、校验失败、审批/取消相关错误不会反复重试。

## Relationship With Agent Planner

阶段六复用阶段五 `run_agent_chat_on_run`。异步提交先创建 `agent_runs`，Worker 读取同一条 run 并执行 Planner 节点，因此 `run_id` 在 API、Trace、Steps、Tool Calls、SQL Logs 和 Reports 之间保持一致。

## Relationship With Approval

当异步任务触发需要审批的工具时：

- Agent Run 保持 `WAITING_APPROVAL`。
- `task_progress.status = WAITING_APPROVAL`。
- 响应中可通过 run traces 和 tool results 追踪 `approval_id`。

审批后自动继续执行预留在后续阶段实现；当前阶段保证审批前不会误标记为成功。

## APIs

- `GET /api/runs/{run_id}/progress`
- `GET /api/tasks/{task_id}/progress`
- `POST /api/runs/{run_id}/cancel`
- `POST /api/tasks/{task_id}/cancel`
- `GET /api/reports`
- `GET /api/reports/{report_id}`
- `GET /api/runs/{run_id}/report`
- `POST /api/reports/{report_id}/export`

导出接口当前返回：

```json
{
  "status": "not_implemented",
  "message": "Report export will be implemented in a later phase.",
  "supported_formats": ["pdf", "docx", "html"]
}
```

## Testing

阶段六新增测试：

- `test_async_agent_run.py`
- `test_task_progress.py`
- `test_task_cancel.py`
- `test_idempotency.py`
- `test_report_history.py`
- `test_async_report_generation.py`

运行：

```bash
PYTHONPATH=backend python3 -m pytest backend/app/tests
```

当前测试覆盖异步提交、进度更新、取消、幂等、报告历史、报告保存 trace 和新增 API 路由。

## Export Roadmap

后续报告导出可以扩展为：

- Markdown to HTML
- Markdown to PDF
- Markdown to DOCX
- 报告版本管理
- 报告下载审计
