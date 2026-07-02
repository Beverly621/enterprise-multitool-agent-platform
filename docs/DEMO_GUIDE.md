# Demo Guide

This guide walks through a local demo from a clean clone to the main multi-step Agent workflow.

## 1. Requirements

- Docker and Docker Compose
- Python 3.12 for local backend development
- Node.js 20+ for frontend development

## 2. Clone

```bash
git clone git@ssh.github.com:Beverly621/enterprise-multitool-agent-platform.git
cd enterprise-multitool-agent-platform
```

## 3. Configure Environment

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

The default configuration uses Mock providers. Real LLM or embedding API keys are optional.

## 4. Start the Stack

```bash
docker compose up -d --build
```

Open:

- Backend Swagger: http://localhost:8100/docs
- Health check: http://localhost:8100/health
- Frontend console: http://localhost:3100

## 5. Seed Demo Data

```bash
bash scripts/seed_demo_data.sh
```

To reset demo records:

```bash
bash scripts/seed_demo_data.sh --reset
```

## 6. Demo Accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@example.com | admin123 |
| Developer | developer@example.com | dev123 |
| User | user@example.com | user123 |
| Guest | guest@example.com | guest123 |

## 7. Upload Demo Documents

Open Knowledge Base in the frontend and upload:

- `data/demo_docs/sample_company_policy.md`
- `data/demo_docs/sample_after_sales_policy.md`
- `data/demo_docs/sample_return_policy.md`
- `data/demo_docs/sample_order_abnormal_handbook.md`

The seed script also creates an indexed demo knowledge base for smoke tests.

## 8. Run Core Demo Questions

Ask in Agent Chat:

```text
员工遇到利益冲突时应该怎么处理？请给出制度依据。
```

Then ask:

```text
哪个地区的异常订单最多？
```

Then ask:

```text
结合最近 30 天订单异常数据和售后知识库生成一份分析报告。
```

## 9. Inspect Trace, Reports and Approvals

After the multi-step report:

1. Open Runs and inspect SQL Node, RAG Node and Report Node.
2. Open Reports and view the generated Markdown report.
3. Ask the Agent to create an email draft from the report.
4. Open Approvals and approve or reject the draft.
5. Open Audit Log and verify important actions are recorded.

## 10. Tests

```bash
cd backend
python -m pytest app/tests
cd ../frontend
npm run build
```

## 11. Public Safety Check

```bash
bash scripts/check_public_safety.sh
```

Review any warnings before publishing.

