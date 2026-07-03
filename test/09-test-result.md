# 09-test-result.md：阶段九验收记录

> 项目：Enterprise Multi-Tool Agent Platform  
> 阶段：09-工程保障、可观测性与评测体系  
> 日期：2026-07-03  
> Docker 强制验收：已于 2026-07-03 补跑通过

## 一、本阶段普通测试结果

命令：

```bash
cd backend
python3 -m pytest app/tests
```

结果：

```text
77 passed, 1 warning
```

说明：warning 来自 passlib 对 Python `crypt` 模块的弃用提示，不影响阶段九功能验收。

## 二、Eval / Regression 结果

命令：

```bash
cd backend
python3 -m app.scripts.run_eval --type rag --no-db
python3 -m app.scripts.run_eval --type sql-guardrails --no-db
python3 -m app.scripts.run_eval --type tool --no-db
python3 -m app.scripts.run_eval --type agent --no-db
python3 -m app.scripts.run_regression --no-db
```

结果：

```text
RAG Eval: 10 passed / 10 total
SQL Guardrails Eval: 22 passed / 22 total, false_negative=0, false_positive=0
Tool Eval: 10 passed / 10 total
Agent Eval: 12 passed / 12 total
Regression: 12 passed / 12 total
```

## 三、前端构建结果

命令：

```bash
cd frontend
npm install
npm run build
```

结果：

```text
Compiled successfully
```

补充：临时安装产生的 `frontend/node_modules` 和构建产物 `frontend/.next` 已在验收后删除，未提交。

## 四、安全检查结果

命令：

```bash
bash scripts/check_public_safety.sh
```

结果：

```text
[OK] No tracked .env file found.
[OK] No common local env file found in the working tree.
[OK] No tracked node_modules, __pycache__, .pytest_cache or .next directory.
[OK] No high-confidence API key/token pattern found.
[WARN] Provider key variable assignment text found. Confirm it is placeholder-only.
[WARN] Generic sensitive words found in docs/data/scripts. Review context before publishing.
```

结论：公开安全检查通过；WARN 为文档和模板中的占位变量及安全说明词汇，发布前仍需人工确认语境。

## 五、Docker 验收状态

状态：已补跑通过。

补验收依据：本地 `test/02-test-result.md`，测试基线 `99570fe feat: add observability and eval system`，修复提交 `cafc9cc fix: stabilize docker milestone validation`。

通过项：

- Docker 冷启动：通过，已执行 `docker compose down -v`、`docker compose build --no-cache`、`docker compose up -d`。
- 容器状态：通过，backend / frontend / celery_worker / postgres / redis 均运行，postgres / redis healthy。
- Alembic 迁移：通过，当前 head 为 `0006_observability_and_eval`。
- Demo seed：通过，首次 seed 成功，第二次 seed 幂等跳过重复数据。
- 后端容器全量测试：通过，`78 passed, 1 warning`。
- 前端容器 lint/build：通过。
- HTTP 冒烟：通过，健康检查、版本、4 个账号登录、同步报告、异步任务、异步报告、tasks/reports/evals/dashboard。
- Celery Worker：通过，任务被接收并执行成功。
- 前端真实 API 联通：通过，`curl -I http://localhost:3100/` 返回 `307 /dashboard`，前端页面与后端 API 冒烟通过。

本阶段保留 Dockerfile、docker-compose.yml、compose.yaml、docker-compose.override.yml 等容器相关配置要求。后续新增依赖或环境变量时，仍必须同步更新 Dockerfile、依赖清单、lockfile 与 `.env.example`。
