# HelloZenno AI Agent Instructions

AI-powered language learning app with interactive vocabulary and audio generation.

See also:
- `README.md` - Project overview and quick start
- `docs/DOCUMENTATION_ORGANISATION.md` - Complete documentation guide
- `docs/PROJECT_STRUCTURE.md` - Directory structure and data flow

## Architecture

**Stack**: SvelteKit frontend + Flask API + Supabase (PostgreSQL + Auth)

**Key files**:
- Backend entry: `backend/api/index.py`
- Frontend routes: `frontend/src/routes/`
- Database models: `backend/db_models.py`
- Migrations: `backend/migrations/`

**Documentation**:
- Architecture: `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`
- Database: `backend/docs/DATABASE.md`, `backend/docs/MODELS.md`
- Auth: `frontend/docs/AUTH.md`

## Coding Principles

See `docs/instructions/CODING-PRINCIPLES.md` for full principles.

Key points:
- Keep changes minimal and focused
- Fix root causes, not symptoms
- Start simple, add complexity later
- Use lowercase type hints (`list[str]` not `List[str]`)

## Key Development Info

### Authentication
- Supabase JWT tokens
- Backend decorators: `@api_auth_required`, `@api_auth_optional`
- See: `frontend/docs/AUTH.md`

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
- See: `frontend/docs/STYLING.md`, `frontend/docs/ENHANCED_TEXT.md`

### Testing & Debugging
- Frontend type check: `cd frontend && npm run check`
- Debug logs: Check `/logs/backend.log` and `/logs/frontend.log`
- See: `backend/docs/DEBUGGING.md`

### AI Development Modes
- See `docs/instructions/` for special modes

## Common Commands

```bash
# Development (user has these running)
source .env.local
./scripts/local/run_backend.sh    # Flask on :3000
./scripts/local/run_frontend.sh   # SvelteKit on :5173

# Type checking
cd frontend && npm run check

# Database
./scripts/local/migrate.sh        # Run migrations
./scripts/local/migrations_list.sh # Check status

# Production
./scripts/prod/deploy.sh          # Deploy
./scripts/prod/backup_db.sh       # Backup DB
```
