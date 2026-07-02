# Frontend Console

阶段七实现了企业后台风格的可视化控制台，让前六个阶段的 RAG、SQL Agent、Tool Calling、Agent Planner、异步任务、报告历史、Trace、Audit 和 RBAC 能通过浏览器完整演示。

## Stage Goal

- 提供可登录、可演示、可截图、可录屏的后台控制台。
- 页面真实调用后端 API，不伪造核心业务结果。
- 用统一 API Client、Token 管理、AuthGuard 和角色菜单支撑所有后台页面。
- 让 Agent Runtime、Run Trace、Task Progress 和 Report History 可视化。

## Tech Stack

- Next.js 16.2.10
- React 19.2.0
- TypeScript
- Tailwind CSS
- lucide-react
- ESLint 9 flat config

`frontend/.env.example` 提供：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8100
NEXT_PUBLIC_APP_NAME=Enterprise Multi-Tool Agent Platform
```

前端不保存或暴露模型 API Key，所有模型调用都经过后端。

## Page Structure

- `/login`: 登录页和 demo 账号提示。
- `/dashboard`: 系统概览、运行数量、报告数量、待审批和失败任务。
- `/kb`: 知识库列表和创建。
- `/kb/[id]`: 知识库详情、文档上传、文档状态、检索和 RAG 测试。
- `/agent`: 统一 Agent Chat 演示入口。
- `/sql-agent`: SQL Agent 安全查询与危险语句测试。
- `/tools`: 工具列表。
- `/tools/[toolName]`: Tool Schema 和调用测试。
- `/approvals`: 审批列表、Approve、Reject。
- `/runs`: Agent Run 列表。
- `/runs/[runId]`: Run 详情、Step Timeline、Trace Timeline、Tool Calls、Task Progress 和 Report Link。
- `/tasks`: 异步任务进度和取消。
- `/reports`: 报告历史。
- `/reports/[reportId]`: Markdown 报告详情和导出预留按钮。
- `/audit`: 审计日志。
- `/admin/users`: 用户和角色展示。

## API Client

`frontend/lib/api.ts` 封装：

- `apiGet<T>()`
- `apiPost<T>()`
- `apiDelete<T>()`
- `login()`
- `currentUser()`

Client 自动读取本地 token 并添加 `Authorization: Bearer <token>`。遇到 401 会清理 token 并跳转 `/login`。

## AuthGuard

`components/layout/AuthGuard.tsx` 负责：

- 检查 localStorage token。
- 调用 `/api/auth/me` 加载用户。
- 未登录跳转 `/login`。
- 加载完成后渲染 sidebar、top nav 和页面内容。

## Role Menu

菜单按角色过滤：

- Guest: Dashboard, Knowledge Base, Agent Chat
- User: Tools, Approvals, Runs, Reports
- Developer: SQL Agent, Tasks, Audit
- Admin: Admin Users 和全部后台能力

## Agent Chat

`/agent` 支持：

- 自然语言输入。
- 选择知识库。
- 同步或异步模式。
- 可输入 `idempotency_key`。
- 展示 intent、answer、run_id、task_id、trace_url、citations、generated_sql、tool_results 和 approval_id。
- async mode 会轮询 `/api/runs/{run_id}/progress` 并展示进度条。

## Run Trace

`/runs/[runId]` 聚合：

- `/api/runs/{run_id}`
- `/api/runs/{run_id}/steps`
- `/api/runs/{run_id}/traces`
- `/api/runs/{run_id}/tool-calls`
- `/api/runs/{run_id}/progress`
- `/api/runs/{run_id}/report`

页面用 timeline 展示 Step 和 Trace，便于解释 Agent 多步骤执行链路。

## Task Progress

`/tasks` 调用 `/api/tasks` 展示异步任务：

- task_id
- run_id
- task_type
- status
- progress
- current_stage
- updated_at

非终态任务可以通过 `/api/tasks/{task_id}/cancel` 取消。

## Reports

`/reports` 和 `/reports/[reportId]` 展示 Markdown 报告历史。导出按钮调用 `/api/reports/{report_id}/export`，当前显示后端返回的 `not_implemented` 预留响应。

## Audit

`/audit` 调用 `/api/audit`，展示 action、resource、created_at 和已脱敏 metadata。后端 RBAC 继续控制访问权限。

## Backend Console APIs

阶段七补齐了前端需要的轻量接口：

- `GET /api/dashboard/summary`
- `GET /api/tasks`
- `GET /api/tool-calls`
- `GET /api/kb/{kb_id}`
- `GET /api/kb/{kb_id}/documents`

这些接口只做汇总或列表，不绕过 RBAC 和已有业务逻辑。

## Local Start

后端：

```bash
bash scripts/run_backend.sh
```

前端：

```bash
cd frontend
npm install
npm run dev
```

默认前端地址为 `http://localhost:3100`，后端 API 地址为 `http://localhost:8100`。

## Demo Flow

1. 使用 `admin@example.com / admin123` 登录。
2. 进入 Dashboard 查看系统概览。
3. 创建知识库并上传示例制度文档。
4. 进入 Agent Chat，询问制度依据类问题。
5. 发送 SQL 分析问题。
6. 发送多步骤报告问题并开启 async mode。
7. 打开 Runs 详情查看 Step 和 Trace。
8. 打开 Tasks 查看异步进度。
9. 打开 Reports 查看 Markdown 报告。
10. 调用 `send_email_draft` 后到 Approvals 页面审批。
11. 打开 Audit 查看审计日志。

## Screenshot Notes

建议阶段八补充截图：

- Login
- Dashboard
- Agent Chat with async progress
- Run Trace detail
- Report detail
- Tool schema and approval flow

## Verification

```bash
cd frontend
npm run lint
npm run build
npm audit --omit=dev
```

后端：

```bash
python3 -m ruff check backend/app backend/alembic
PYTHONPATH=backend python3 -m pytest backend/app/tests
```

## Future Improvements

- 更细粒度的前端 RBAC 控件禁用状态。
- Run 详情页增加 SQL Log 专区。
- 报告导出 PDF/DOCX。
- WebSocket 或 SSE 实时任务进度。
- 前端 E2E 测试。
