# Enterprise Multi-Tool Agent Platform - Stage 9 README

当前完成阶段：阶段九：工程保障、可观测性与评测体系。

## 本阶段交付

- 新增 `provider_calls`、`eval_cases`、`eval_runs`、`eval_results`、`runtime_metrics_daily` 模型与 Alembic migration。
- 新增 Provider 调用指标记录，Mock Provider 成本固定为 `0`，错误信息写入前脱敏。
- 新增 Metrics API：`/api/metrics/summary`、`/api/metrics/agent-runs`、`/api/metrics/rag`、`/api/metrics/sql-guardrails`、`/api/metrics/tools`、`/api/metrics/tasks`、`/api/metrics/providers`。
- 新增 Eval API：`/api/evals/runs`、`/api/evals/runs/{eval_run_id}`。
- 新增 RAG / SQL Guardrails / Tool / Agent / Regression JSONL 数据集。
- 新增 `run_eval.py`、`run_regression.py`、`export_eval_report.py`。
- 增强前端 Dashboard 指标卡：Agent 成功率、平均/P95 耗时、RAG 查询数、SQL 拦截数、Tool 成功率、异步任务成功率、报告数、Provider 调用数、估算成本。
- 新增可观测性与评测文档、指标定义、回归测试指南和评测报告模板。

## 数据集规模

- RAG Eval：10 条。
- SQL Guardrails Eval：22 条，覆盖安全 SELECT、危险 DML/DDL、敏感表字段、多语句、注释绕过、子查询访问敏感表等。
- Tool Eval：10 条。
- Agent Eval：12 条。
- Regression：12 条。

## 推荐命令

```bash
cd backend
python -m pytest app/tests
python -m app.scripts.run_eval --type rag --no-db
python -m app.scripts.run_eval --type sql-guardrails --no-db
python -m app.scripts.run_eval --type tool --no-db
python -m app.scripts.run_eval --type agent --no-db
python -m app.scripts.run_regression --no-db
```

前端：

```bash
cd frontend
npm run build
```

公开安全检查：

```bash
bash scripts/check_public_safety.sh
```

## 本阶段验收记录

- 本阶段普通测试结果：`cd backend && python3 -m pytest app/tests`，结果 `77 passed, 1 warning`。
- Eval / Regression 结果：RAG 10/10 passed；SQL Guardrails 22/22 passed，`false_negative=0`；Tool 10/10 passed；Agent 12/12 passed；Regression 12/12 passed。
- 前端构建结果：`cd frontend && npm run build`，结果 `Compiled successfully`。
- 安全检查结果：`bash scripts/check_public_safety.sh`，结果通过；仅提示 provider key 占位变量和 token/secret/password 等安全说明词汇需要发布前人工确认语境。
- Docker 验收状态：待最终补跑。当前阶段未标记 Docker 验收通过，未删除或弱化 `02-test.md` 中 Docker 冷启动、容器内 DB/Celery/API 联通、seed 幂等、前端真实 API 联通验收要求。

## Docker 遗留项

当前机器暂不进行 Docker 强制验收。最终交付前必须回到 `02-test.md`，完整补跑：

- Docker 冷启动。
- 容器内 DB / Celery / API 联通。
- seed 幂等。
- 前端真实 API 联通验收。

Dockerfile、docker-compose.yml、compose.yaml、docker-compose.override.yml 等容器相关配置不得删除或弱化。后续新增依赖和环境变量时，必须同步更新 Dockerfile、依赖清单、lockfile 与 `.env.example`。
