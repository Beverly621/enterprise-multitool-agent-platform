# Database Design

Stage 1 creates the core enterprise agent platform schema with Alembic.

## Core Tables

- Identity and RBAC: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`
- Knowledge base: `knowledge_bases`, `documents`, `document_chunks`
- Agent runtime: `agent_runs`, `agent_steps`, `tool_calls`, `agent_traces`
- Tools and approvals: `agent_tools`, `tool_permissions`, `approvals`
- Governance: `sql_query_logs`, `audit_logs`
- Conversation UX: `conversations`, `messages`, `user_preferences`

`document_chunks.embedding` uses pgvector with the configured default dimension of `1536`.

