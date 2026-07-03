# Metrics Definition

`success_rate`: successful items divided by total items.

`failure_rate`: failed items divided by total items.

`avg_duration_ms`: arithmetic mean execution duration in milliseconds.

`p95_duration_ms`: 95th percentile execution duration in milliseconds.

`retrieval_hit`: whether RAG TopK retrieval contains the expected source.

`keyword_match`: whether the generated answer or validated expected payload contains required keywords.

`citation_present`: whether a RAG response includes at least one citation.

`false_positive`: a safe SQL query blocked by Guardrails.

`false_negative`: a dangerous SQL query allowed by Guardrails. This is a blocking security issue.

`tool_success_rate`: successful tool calls divided by total tool calls.

`estimated_cost`: approximate provider cost based on token estimates or SDK usage. Mock provider cost is always `0`.

`provider_latency_ms`: elapsed provider request time in milliseconds.

`async_task_success_rate`: successful async tasks divided by total async tasks.

`sql_block_rate`: blocked SQL queries divided by total SQL queries.
