# Enterprise Multi-Tool Agent Platform - Stage 10 README

当前完成阶段：阶段十：部署、CI-CD 与生产化配置。

## 本阶段交付

- 新增生产 Docker Compose：`deploy/docker-compose.prod.yml`。
- 新增 Nginx 反向代理与安全 Headers 预留：`deploy/nginx.conf`。
- 新增 Render / Railway / Fly.io / Vercel 部署参考文件。
- 新增 backend / frontend `.dockerignore`。
- 优化 backend / frontend Dockerfile，前端支持生产 standalone 镜像。
- 新增环境变量检查脚本：`scripts/check_env.sh`、`backend/scripts/check_env.py`、`frontend/scripts/check_env.js`。
- 新增后端 prestart：环境检查、等待 DB/Redis、迁移、可选 seed、启动服务。
- 新增 GitHub Actions：backend CI、frontend CI、docker build、public safety。
- 新增部署前检查与 Docker smoke test 脚本。
- 新增部署、CI/CD、生产检查清单、环境变量与故障排查文档。
- 后端新增安全 Headers，并支持通过 `FRONTEND_ORIGIN` 控制 CORS。

## 阶段十验收记录

- 环境变量检查：`bash scripts/check_env.sh`，通过。
- 后端测试：`cd backend && python3 -m pytest app/tests`，结果 `87 passed, 1 warning`。
- 前端 lint：`cd frontend && npm run lint`，通过。
- 前端 build：`cd frontend && npm run build`，结果 `Compiled successfully`。
- 开发 Docker build：`docker compose build`，通过。
- 生产 Docker build：`docker compose -f deploy/docker-compose.prod.yml build`，通过。
- Docker smoke test：`bash scripts/docker_smoke_test.sh`，通过，覆盖 compose 冷启动、`/health`、`/api/version`、seed、登录、Agent Chat、前端 HTTP。
- Pre-deploy check：`bash scripts/pre_deploy_check.sh`，通过。
- 公开安全检查：`bash scripts/check_public_safety.sh`，通过；仅保留 provider key 占位变量与 token/secret/password 等安全说明词汇的人工语境确认 warning。

验收后已清理 `frontend/node_modules`、`frontend/.next`、`.pytest_cache`、`__pycache__` 等临时产物。

## 安全说明

- 未提交真实 `.env`、API Key、token、secret。
- Mock Provider 模式不要求真实模型 API Key。
- 真实 Provider 的 API Key 仅能通过部署平台变量或本地未跟踪 `.env` 配置。
- 前端 `NEXT_PUBLIC_*` 只允许公开配置，不允许放模型密钥。

## 下一阶段

阶段十一将进入简历包装、文档完善与演示材料。
