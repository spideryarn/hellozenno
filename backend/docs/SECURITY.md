# Backend Security

## Scope
- Flask API, Peewee ORM, Supabase (PostgreSQL + Auth)

## Practices
- Auth: Supabase JWT; decorators `@api_auth_required`, `@api_auth_optional`
- Logging: Loguru to `/logs/backend.log`
- Config from `.env.*` via `python-dotenv`
- Dependencies pinned/modern; prefer binary wheels in CI

## Scanning
- One-off SCA: `python -m pip_audit -r backend/requirements.txt`
- Optional static analysis: `bandit -q -r backend`

## CI Gate
- GitHub Actions job `backend-pip-audit` runs `pip-audit` on pushes/PRs to `main`
- Fails build on discovered vulns

## Local Commands
```bash
cd backend
python -m pip_audit -r requirements.txt
```

## Incident/Updates
- Fix critical within 48h; high within 7 days
- Commit lockfile/requirements updates and re-run CI
