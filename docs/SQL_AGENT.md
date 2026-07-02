# SQL Agent

Stage 3 implements a guarded Text-to-SQL subsystem for structured demo business data.

## Goal

The SQL Agent converts natural-language business questions into safe PostgreSQL `SELECT` queries, executes them against demo e-commerce tables, explains the result, and records full trace, audit and query logs.

## Demo Business Tables

- `demo_customers`: customer id, name, state, city and creation time. `email` exists in the physical table but is blocked by Guardrails.
- `demo_products`: product id, name, category, department and price.
- `demo_orders`: order status, purchase date, delivery dates, payment value, seller and state.
- `demo_order_items`: order-product-seller item details.
- `demo_reviews`: review score and comments. `review_score <= 2` means low-score abnormality.
- `demo_after_sales`: after-sales issue type and status.

Seed demo data:

```bash
cd backend
python -m app.seed.seed_demo_orders
```

The seed creates at least 200 orders and is idempotent.

## Abnormal Order Definition

An order is abnormal when any of these conditions are true:

- `order_status in ('canceled', 'unavailable')`
- `order_delivered_customer_date > order_estimated_delivery_date`
- `review_score <= 2`
- an after-sales `issue_type` exists
- `payment_value` is more than twice the average payment value

## Schema Reader

`schema_reader.py` exposes only the approved `demo_*` tables with human-readable column descriptions. It does not expose `users`, RBAC tables, RAG tables, audit tables, traces, migration tables or system tables.

## SQL Generation

The prompt requires JSON output with `sql` and `explanation`. Mock mode uses deterministic keyword routing so local demos work without API keys and covers abnormal orders, region/state, low score, after-sales, product category and delivery delay questions.

## Guardrails

`sql_guardrails.py` combines `sqlparse`, keyword checks, table allowlists and sensitive field checks.

Rules:

- only one `SELECT` statement
- no `DELETE`, `UPDATE`, `INSERT`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT` or `REVOKE`
- no multi-statement SQL
- no `SELECT *`
- only approved `demo_*` tables
- no sensitive fields such as `email`, `password_hash`, `token`, `secret`, `api_key`, `phone`, `address`
- `LIMIT` is required and automatically added or clamped to `100`

## Executor

`sql_executor.py` accepts only Guardrails-cleaned SQL, executes in a read-only style path, attempts a PostgreSQL statement timeout, caps returned rows to 100 and converts results into JSON:

```json
{
  "columns": ["state", "abnormal_count"],
  "rows": [{"state": "SP", "abnormal_count": 23}],
  "row_count": 1,
  "duration_ms": 35
}
```

## Permissions

- Guest: cannot call SQL Agent.
- User: can query demo business tables and see own logs.
- Developer: can query and view SQL logs.
- Admin: full access.

## Logs And Audit

Every SQL Agent query writes:

- `agent_runs`
- `agent_steps`
- `agent_traces`
- `sql_query_logs`
- `audit_logs`

Blocked SQL is logged with `blocked_reason`; result previews store only the first five rows.

## API

Query:

```http
POST /api/sql-agent/query
```

```json
{
  "question": "哪个地区的异常订单最多？"
}
```

Schema:

```http
GET /api/sql-agent/schema
```

Logs:

```http
GET /api/sql-agent/logs
GET /api/sql-agent/logs/{id}
```

## Tests

```bash
cd backend
python -m pytest app/tests
```

