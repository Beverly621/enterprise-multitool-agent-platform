# 09-test-result.md：阶段九验收记录

> 项目：Enterprise Multi-Tool Agent Platform  
> 阶段：09-工程保障、可观测性与评测体系  
> 日期：2026-07-03  
> Docker 强制验收：待最终补跑

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

状态：待最终补跑。

本阶段根据当前机器条件未执行 Docker 强制验收，且不得标记为通过。最终交付前必须回到 `02-test.md`，完整补跑：

- Docker 冷启动。
- 容器内 DB / Celery / API 联通。
- seed 幂等。
- 前端真实 API 联通验收。

本阶段未删除、弱化或跳过 `02-test.md` 中 Docker 强制验收要求，未删除 Dockerfile、docker-compose.yml、compose.yaml、docker-compose.override.yml 等容器相关配置。
