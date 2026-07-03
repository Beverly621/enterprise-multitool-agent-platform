# Final Release Guide

## 1. Pre-Release Checks

Run all final checks from a clean working tree:

```bash
python3 -m pytest backend/app/tests
cd frontend && npm install && npm run build
cd ..
bash scripts/check_public_safety.sh
bash scripts/final_public_safety_check.sh
bash scripts/final_repo_check.sh
bash scripts/final_smoke_test.sh
```

Then remove generated local artifacts such as `frontend/node_modules`, `frontend/.next`, pytest caches and Python `__pycache__` directories.

## 2. Create Release Tag

Create the tag only after `03-test.md` passes:

```bash
git tag -a v1.0.0-demo -m "Enterprise Multi-Tool Agent Platform demo release"
git push origin v1.0.0-demo
```

Do not create the tag before final validation.

## 3. Write Release Notes

Use `RELEASE_NOTES.md` as the source. Keep the wording honest:

- Demo-ready project.
- Simulated data.
- Mock providers by default.
- No claim of live production deployment.
- No fake customer usage or performance metrics.

## 4. Confirm GitHub Page Display

- Open the repository page.
- Confirm README sections render correctly.
- Confirm Mermaid diagrams render.
- Confirm links to docs, deploy files and scripts work.
- Confirm screenshots section says screenshots are pending if no real screenshots are committed.

## 5. Confirm README Links

Check links for:

- `docs/DEMO_GUIDE.md`
- `docs/ARCHITECTURE_OVERVIEW.md`
- `docs/RESUME_DESCRIPTION.md`
- `docs/INTERVIEW_QA.md`
- `docs/FINAL_CHECKLIST.md`
- `docs/THIRD_VALIDATION_PREP.md`
- `RELEASE_NOTES.md`
- `LICENSE`

## 6. Confirm No Sensitive Information

Run:

```bash
bash scripts/check_public_safety.sh
bash scripts/final_public_safety_check.sh
git ls-files | grep -E '(^|/)\.env($|\.|/)' || true
```

Only `.env.example` files should appear in Git.

## 7. Roll Back Release

If a release tag is created too early:

```bash
git tag -d v1.0.0-demo
git push origin :refs/tags/v1.0.0-demo
```

If a sensitive file was published, rotate the leaked secret immediately and clean Git history before re-publishing.
