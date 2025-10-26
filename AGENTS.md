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
- Frontend: `cd frontend && npm run check`
- Backend: `ruff check backend/`, `black backend/`

### Debugging
- Logs: `/logs/backend.log`, `/logs/frontend.log`
- See: `backend/docs/DEBUGGING.md`

### Git Workflow
- Atomic commits: `git reset HEAD unwanted && git add wanted && git commit -m "type: message"`
- See: `gjdutils/docs/instructions/GIT_COMMIT_CHANGES.md`

### AI Development Modes
- See `docs/instructions/` for special modes

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
- If port 5173 is in use: `lsof -ti:5173 | xargs kill -9` or run on 5174 with `cd frontend && PORT=5174 npm run dev`.

- Flask backend should auto-reload on Python changes in development, but it can occasionally get stuck. If changes don't show up, restart `./scripts/local/run_backend.sh`.
