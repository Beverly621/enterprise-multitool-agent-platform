# Third Validation Preparation

This document prepares the final `03-test.md` full validation. Phase 12 does not replace `03-test.md`; it makes the project ready for it.

## 1. Final Validation Scope

Validate phases 1 through 12 from a clean clone, including backend, frontend, Docker, demo data, Agent workflows, observability, CI/CD, docs, safety and presentation materials.

## 2. Fresh Clone Validation

- Clone the public repository.
- Check out `main`.
- Confirm no local untracked secrets are required.
- Copy `.env.example` and `frontend/.env.example`.

## 3. Docker Cold Start

- Run `docker compose down -v`.
- Run `docker compose up -d --build`.
- Wait for backend health.
- Verify PostgreSQL, Redis, backend, Celery and frontend services.

## 4. Demo Data Validation

- Run `bash scripts/seed_demo_data.sh`.
- Re-run it to confirm idempotency.
- Confirm demo knowledge base, users, tools and simulated order data exist.

## 5. RAG / SQL / Tool / Agent / Async Validation

- Upload or use seeded demo documents.
- Run a RAG question.
- Run a SQL Agent analytics question.
- Invoke safe tools.
- Trigger approval-required email draft.
- Run multi-step report generation.
- Verify async progress where applicable.

## 6. Frontend Console Validation

Check `/dashboard`, `/kb`, `/agent`, `/sql-agent`, `/tools`, `/approvals`, `/runs`, `/tasks`, `/reports`, `/audit` and `/admin/users`.

## 7. Metrics / Eval Validation

- Open metrics APIs.
- Run eval or regression commands.
- Confirm provider metrics do not expose secrets.

## 8. CI/CD Validation

Confirm GitHub Actions files exist and local equivalents pass:

- backend tests
- frontend lint/build
- Docker build
- public safety

## 9. README / Docs Validation

Confirm README and docs accurately describe implemented behavior and do not claim production deployment, real users, real customers or fake screenshots.

## 10. Sensitive Information Validation

Run `scripts/check_public_safety.sh`, `scripts/final_public_safety_check.sh` and inspect tracked files for `.env`, keys, tokens, logs, caches and build artifacts.

## 11. Resume Material Validation

Review `docs/RESUME_DESCRIPTION.md`, `docs/INTERVIEW_QA.md`, `docs/DEMO_SCRIPT.md`, `docs/STAR_PROJECT_STORY.md` and `docs/FINAL_PRESENTATION_GUIDE.md` for honest, non-exaggerated claims.
