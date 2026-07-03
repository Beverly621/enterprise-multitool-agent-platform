# Regression Test Guide

## Run Regression

```bash
cd backend
python -m app.scripts.run_regression
```

For local checks without database writes:

```bash
cd backend
python -m app.scripts.run_regression --no-db
```

## Run Eval Suites

```bash
cd backend
python -m app.scripts.run_eval --type rag
python -m app.scripts.run_eval --type sql-guardrails
python -m app.scripts.run_eval --type tool
python -m app.scripts.run_eval --type agent
```

## Add a Case

Add one JSON object per line to the relevant file in `backend/app/evals/`.

Required fields:

- `case_id`: stable unique ID.
- Input fields such as `query`, `sql`, `tool_name` or `args`.
- Expected fields such as `expected_intent`, `expected_safe` or `expected`.

## Interpret Failures

- RAG failures usually mean source coverage, keyword expectation or citation behavior changed.
- SQL Guardrails failures with `false_negative > 0` are blocking security issues.
- Tool failures usually mean metadata, permissions, approval rules or Guardrails integration changed.
- Agent regression failures usually mean intent routing changed and demo flows should be reviewed.

## Update Expected Values

Only update expected values when the new behavior is intentionally designed, reviewed, and documented. Never update expected values to hide a regression.

## Blocking Failures

- Dangerous SQL allowed.
- Sensitive data appears in trace, audit, metrics or eval output.
- Provider calls stop recording.
- Core demo intents no longer route.
- Frontend build fails.
- Docker cold-start and container integration acceptance regresses after the 2026-07-03 passing validation.
