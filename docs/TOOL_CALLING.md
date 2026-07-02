# Tool Calling Platform

阶段四实现标准化 Tool Calling 平台。平台只执行代码库内置的白名单工具，不支持用户上传或动态执行 Python 代码；管理员可以注册工具元数据，但当前阶段不执行任意外部 endpoint。

## Built-in Tools

| Tool | Role | Approval | Purpose |
| --- | --- | --- | --- |
| `search_knowledge_base` | Guest+ | No | 调用阶段二 RAG 向量检索 |
| `execute_safe_sql` | Developer+ | No | 调用阶段三 SQL Guardrails 和只读 SQL Executor |
| `query_order_status` | User+ | No | 查询 demo 订单状态、延迟、评分和售后 |
| `query_after_sales` | User+ | No | 查询 demo 售后工单 |
| `generate_report` | User+ | No | 生成 Markdown 业务报告 |
| `send_email_draft` | User+ | Yes | 创建邮件草稿并等待人工审批，不真实发送 |
| `create_todo` | User+ | No | 创建用户待办 |

## Execution Flow

1. `ToolRegistry.sync_builtin_tools()` 将内置工具 Schema、权限等级、超时和审批策略同步到 `agent_tools`。
2. `ToolExecutor.invoke_tool()` 创建 `tool_calls` 记录。
3. 执行权限校验：Guest < User < Developer < Admin。
4. 使用 JSON Schema 校验参数，拒绝缺失字段、类型错误和多余字段。
5. 对 `require_approval=true` 的工具创建 `approvals` 记录并返回 `WAITING_APPROVAL`。
6. 对普通工具执行超时和重试控制，写入 `tool_result`、`agent_traces` 和 `audit_logs`。

## APIs

- `GET /api/tools`
- `GET /api/tools/{tool_name}`
- `POST /api/tools/register`
- `POST /api/tools/{tool_name}/enable`
- `POST /api/tools/{tool_name}/disable`
- `POST /api/tools/{tool_name}/invoke`
- `GET /api/tool-calls/{tool_call_id}`
- `GET /api/runs/{run_id}/tool-calls`
- `GET /api/approvals`
- `GET /api/approvals/{approval_id}`
- `POST /api/approvals/{approval_id}/approve`
- `POST /api/approvals/{approval_id}/reject`

## Trace And Audit

工具执行写入 `agent_traces`，核心事件包括：

- `TOOL_CALL_STARTED`
- `TOOL_PERMISSION_CHECKED`
- `TOOL_ARGS_VALIDATED`
- `TOOL_WAITING_APPROVAL`
- `TOOL_CALL_RETRY`
- `TOOL_CALL_SUCCESS`
- `TOOL_CALL_FAILED`
- `TOOL_CALL_TIMEOUT`

审计日志写入 `audit_logs`，包括：

- `TOOL_REGISTERED`
- `TOOL_DISABLED`
- `TOOL_ENABLED`
- `TOOL_INVOKED`
- `TOOL_APPROVAL_CREATED`
- `TOOL_APPROVED`
- `TOOL_REJECTED`
- `TOOL_FAILED`

## Example

Invoke an approval-required tool:

```http
POST /api/tools/send_email_draft/invoke
Authorization: Bearer <token>
Content-Type: application/json

{
  "args": {
    "to_email": "manager@example.com",
    "subject": "订单异常分析报告",
    "body": "请查看本周订单异常分析。"
  }
}
```

Response returns `WAITING_APPROVAL` and an `approval_id`. Approve it with:

```http
POST /api/approvals/{approval_id}/approve
Authorization: Bearer <token>

{
  "reason": "Approved for internal review."
}
```
