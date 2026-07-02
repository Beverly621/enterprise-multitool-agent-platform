# GitHub Public Checklist

Run this checklist before publishing or tagging a release.

## Sensitive Files

- [ ] `.env` is not tracked.
- [ ] `.env.local` is not tracked.
- [ ] `.env.*` files are not tracked except `.env.example`.
- [ ] Real API keys are not committed.
- [ ] Tokens, secrets, cookies and private credentials are not committed.
- [ ] Real database URLs or server addresses are not committed.

## Data Safety

- [ ] Demo order data is simulated.
- [ ] No real enterprise order data is committed.
- [ ] No real customer complaint records are committed.
- [ ] No real personal data is committed.
- [ ] Public source links are documented in `docs/PUBLIC_DATA_SOURCES.md`.

## Generated Files

- [ ] `node_modules/` is not tracked.
- [ ] `__pycache__/` is not tracked.
- [ ] `.pytest_cache/` is not tracked.
- [ ] `.next/` is not tracked.
- [ ] `.DS_Store` is not tracked.

## Demo Readiness

- [ ] `README.md` startup steps are accurate.
- [ ] `.env.example`, `backend/.env.example` and `frontend/.env.example` are complete.
- [ ] `docker compose up -d --build` starts the stack.
- [ ] `bash scripts/seed_demo_data.sh` runs successfully.
- [ ] Demo accounts work.
- [ ] Knowledge-base demo documents can be uploaded.
- [ ] Multi-step report demo runs from Agent Chat.
- [ ] Run Trace and Reports show the result.
- [ ] `send_email_draft` requires approval and does not send real email.

## Automated Checks

- [ ] `bash scripts/check_public_safety.sh` passes.
- [ ] `cd backend && python -m pytest app/tests` passes.
- [ ] `cd frontend && npm run build` passes.

