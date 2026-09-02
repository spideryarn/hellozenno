# HelloZenno AI Agent Instructions

AI-powered language learning app with interactive vocabulary and audio generation.

See also:
- `README.md` - Project overview and quick start
- `docs/DOCUMENTATION_ORGANISATION.md` - Complete documentation guide
- `docs/reference/PROJECT_STRUCTURE.md` - Directory structure and data flow

## Project Navigation

**Core directories**:
- `frontend/` - SvelteKit app (routes in `src/routes/`)
- `backend/` - Flask API (entry: `api/index.py`)
- `docs/` - Documentation (instructions, planning, reference)
- `scripts/` - Build and deployment scripts
- `logs/` - Application logs

## Architecture

**Stack**: SvelteKit frontend + Flask API + Supabase (PostgreSQL + Auth)

**Key files**:
- Backend entry: `backend/api/index.py`
- Frontend routes: `frontend/src/routes/`
- Database models: `backend/db_models.py`
- Migrations: `backend/migrations/`

**Essential docs**:
- Architecture: `docs/reference/ARCHITECTURE.md`, `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`
- Database: `backend/docs/DATABASE.md`, `backend/docs/MODELS.md`
- Auth: `frontend/docs/AUTHENTICATION_AUTHORISATION.md`
- API: `frontend/docs/BACKEND_FLASK_API_INTEGRATION.md`

## Coding Principles

See `docs/instructions/CODING-PRINCIPLES.md` for full principles.

Key points:
- Keep changes minimal and focused
- Fix root causes, not symptoms
- Start simple, add complexity later
- Raise errors early (avoid try/except wrapping)
- Comment sparingly
- Use lowercase type hints (`list[str]` not `List[str]`)

## Key Development Info

### Authentication
- Supabase JWT tokens
- Backend decorators: `@api_auth_required`, `@api_auth_optional`
- See: `frontend/docs/AUTHENTICATION_AUTHORISATION.md`

### Environment
- `.env.local` (development)
- `.env.testing` (test)
- `.env.prod` (production)

### Database
- PostgreSQL via Supabase
- Peewee ORM
- Migrations: `./scripts/local/migrate.sh`
- See: `backend/docs/MIGRATIONS.md`

### Logging
- Backend: `/logs/backend.log` (Loguru)
- Frontend: `/logs/frontend.log`
- Usage: `from loguru import logger`

### Frontend
- **Styling**: Bootstrap dark theme, `--hz-color-*` variables
- **Components**: Enhanced text, DataGrid, Cards
- **API**: Type-safe with generated routes
- See: `frontend/docs/VISUAL_DESIGN_STYLING.md`, `frontend/docs/ENHANCED_TEXT.md`

### Testing
- Backend: `pytest backend/tests/`
- See: `docs/reference/TESTING.md`, `backend/docs/BACKEND_TESTING.md`
- Local test user credentials: `docs/reference/LOCAL_TEST_USERS.md`

### Type Checking & Linting
Config lives in the root `pyproject.toml` (`[tool.ruff]`, `[tool.black]`), so run these
from the repo root and they pick it up automatically. `gjdutils/` is excluded from both.

```bash
source /Users/greg/.venvs/hellozenno__backend/bin/activate
ruff check .                       # lint (pass `--fix` to auto-fix)
ruff check --select E9,F63,F7,F82 .  # fatal-only subset; this one is CLEAN, keep it that way
black .                            # format (`black --check --diff .` to preview)
cd frontend && npm run check       # svelte-check; CLEAN, keep it that way
cd frontend && npm run lint        # prettier --check + eslint (`npm run format` to fix)
```

Known baseline (don't be alarmed, and please don't "fix" it in an unrelated PR):
- `ruff check .` reports ~261 findings, mostly unused imports/variables.
- `black --check .` wants to reformat ~84 files (was ~52 under black 25.1.0).
- `npm run lint` fails on ~211 prettier formatting diffs.

CI (`.github/workflows/lint-and-typecheck.yml`) runs all of these. Only the fatal ruff
subset and `npm run check` block a PR; the rest are advisory until the backlog is
cleared. If you clear one, flip its `continue-on-error` off in the same commit.

### Frontend dependency overrides

`frontend/package.json` has an `overrides` block. Every entry exists to hold a package at a
version that was *already soaked* when the 2026-08-31 Dependabot critical/high sweep landed -
npm otherwise resolves to the highest version a parent range allows, which at the time meant
picking up releases only a day or two old. The lockfile alone would pin these, but the
overrides record the intent so a later `npm update` cannot quietly undo it.

| entry | held at | why |
|---|---|---|
| `js-yaml` | 4.3.1 | 4.3.2 landed 2026-08-26 |
| `devalue` | 5.9.1 | 5.9.2 landed 2026-08-27; kit 2.70.x needs `^5.8.1` |
| `rollup` | 4.59.1 | 4.63.1 landed 2026-08-28 |
| `brace-expansion@1` | 1.1.18 | scoped to the 1.x line; 2.x consumers need `^2.0.1` |
| `picomatch@2` / `picomatch@4` | 2.3.2 / 4.0.5 | 4.0.6 and 4.0.7 both landed 2026-08-24 |
| `ast-types` | 0.16.1 | dormant since 2022, then 0.16.2 AND 0.16.3 both published 2026-08-30 |

**Revisit from 2026-09-07**, once these have aged. Remove entries one at a time, re-run
`npm install && npm audit --audit-level=high && npm run check`, and drop the row above.
Before unpinning `ast-types`, diff 0.16.1...0.16.3 and run `npm audit signatures`.

### Debugging
- Logs: `/logs/backend.log`, `/logs/frontend.log`
- Production (Vercel) runtime logs: `timeout 30 vercel logs https://api.hellozenno.com`
  (or `https://www.hellozenno.com`). The `timeout` matters - it live-tails and never exits.
- See: `backend/docs/DEBUGGING.md`

### Git Workflow
- Atomic commits: `git reset HEAD unwanted && git add wanted && git commit -m "type: message"`
- See: `gjdutils/docs/instructions/GIT_COMMIT_CHANGES.md`

### AI Development Modes
- See `docs/instructions/` for special modes
- See `docs/generic/CHIEF_ENGINEER.md` for complex multi-phase workflow

### Codex CLI as a subagent
For a cross-family (GPT) review or a delegated editing task, drive Codex via the wrapper —
never bare `codex exec`, which wedges on stdin and floods your context:
```bash
node scripts/run-codex.ts --model gpt-5.6-sol --effort high --prompt-file <task> --output <answer>
```
Read-only by default; `--sandbox workspace-write` to let it edit (commit or stash first). Always
check the answer file is non-empty — exit 0 with no answer is a failure that looks like agreement.
See `docs/reusable/codex-cli-as-subagent.md`.

### Triple Review
When asked to "use triple-review", invoke ALL THREE reviewers in parallel:
- `@reviewer-gpt5.2-high` - Primary reviewer (thorough, high reasoning)
- `@reviewer-gemini` - Secondary reviewer (alternative perspective)
- `@reviewer-opus` - Deep reviewer (nuanced analysis)

Proceed if all reviewers >= 80% confidence; refine if any < 80%.

## Common Commands

```bash
# Development (user has these running)
source .env.local
supabase start                     # requires Docker Desktop
export FLASK_PORT=3000
./scripts/local/run_backend.sh     # Flask on :3000
./scripts/local/run_frontend.sh    # SvelteKit on :5173
open -a "Google Chrome" http://localhost:5173

# Type checking
cd frontend && npm run check

# Database
./scripts/local/migrate.sh         # Run migrations
./scripts/local/migrations_list.sh # Check status

# Production
source /Users/greg/.venvs/hellozenno__backend/bin/activate
./scripts/prod/deploy.sh           # Deploy (see backend/docs/DEVOPS.md)
./scripts/prod/backup_db.sh        # Backup DB
```

Tip:
- If port 5173 is in use, find out who holds it first with `lsof -nP -iTCP:5173 -sTCP:LISTEN` - on Greg's shared remote box it is probably another project's dev server, and killing it destroys somebody else's work. Run on 5174 instead: `cd frontend && PORT=5174 npm run dev`.

- Flask backend should auto-reload on Python changes in development, but it can occasionally get stuck. If changes don't show up, restart `./scripts/local/run_backend.sh`.
