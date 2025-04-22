# HelloZenno Project Reference

To understand more about the purpose of the app, see `./README.md`

## Project Architecture

HelloZenno has transitioned from a Flask/Jinja/Svelte application to a SvelteKit/TypeScript frontend with a Flask API and Supabase backend:

see `frontend/docs/README.md` for a good high-level intro, and references to other files.

## Coding

**Core principles**

- Prioritise simplicity, debuggability, and readability. Try to keep things concise, don't over-comment, over-log, or over-engineer.
- Aim to keep changes minimal, and focused on the task at hand.
- Fix the root cause in a clean way, rather than bandaids/hacks.
- By default, raise errors early, clearly & fatally. Prefer not to wrap in try/except.
- Aim to reuse code, and use sub-functions to make long/complex functions clearer.
- Comment sparingly - reserve it for explaining surprising or confusing sections.
- Always start simple, get a v1 working, and then gradually add complexity.
- If things don't make sense or seem like a bad idea, ask questions or discuss rather than just going along with it.


- **Backend (Flask + PostgreSQL)**
  - `api/index.py` - Main Flask application entry point
  - `views/` - Route handlers and API functions
  - `utils/` - Helper functions
  - `db_models.py` - Database models (using Peewee ORM)
  - `migrations/` - Database migration scripts

- **SvelteKit Frontend**
  - See `frontend/README.md` for detailed documentation
  - Documentation for specific aspects:
    - `frontend/docs/SETUP.md` - Installation and development
    - `frontend/docs/STYLING.md` - Bootstrap theming and component usage
    - `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md` - Architecture overview
    - `frontend/docs/AUTH.md` for info on login/signup, and especially auth_optional/auth_required
    - `frontend/docs/BACKEND_FLASK_API_INTEGRATION.md` - API integration
  - Structure:
    - `frontend/src/routes/` - SvelteKit routes and pages
    - `frontend/src/lib/components/` - Reusable Svelte components
    - `frontend/src/lib/generated/routes.ts` - Auto-generated API route types
    - `frontend/static/` - Static assets and CSS

## Development Guidelines

### Database
- see `DATABASE.md`, and also use the Supabase MCP (read-only)
- see `MIGRATIONS.md` before creating or running migrations

### Logging
- **Backend logs**: `/logs/backend.log` (managed by Loguru via LimitingFileWriter)
- **SvelteKit logs**: `/logs/frontend.log` (captured from SvelteKit development server)
- Use the `loguru` library for Python logging: see `utils/logging_utils.py` and `scripts/local/run_backend.sh` (backend) and `scripts/local/run_frontend.sh` (frontend)

### Frontend Components

#### SvelteKit Component Library

The SvelteKit frontend uses reusable Bootstrap-styled components.

see `frontend/docs/SITE_ORGANISATION.md` and `frontend/docs/STYLING.md` for detailed component usage.

#### Type-Safe API Integration

The SvelteKit frontend uses type-safe API integration with the Flask backend:

- Flask generates TypeScript type definitions in `frontend/src/lib/generated/routes.ts` - see `backend/docs/URL_REGISTRY.md`
- SvelteKit uses the `getApiUrl()` and `getPageUrl()` and `apiFetch()` function to generate properly typed API URLs
- All API endpoints follow a standard structure

See `frontend/docs/FLASK_API_INTEGRATION.md` for details.

### Browser Testing and Web Search with cursor-tools

use Playwright MCP for investigating frontend issues

#### Web Search

use Perplexity_ask MCP to find out about stuff

You can also use Fetch_url MCP to retrieve particular urls.


### Testing

[THIS IS A BIT OUT OF DATE - we haven't updated the automated tests in a while]

see `docs/TESTING.md`

### Database

see `backend/docs/DATABASE.md` and `backend/docs/MIGRATIONS.md`

e.g.

```bash
# Connect to local database with nice formatting
psql -d hellozenno_development -P pager=off -x auto

# One-off queries
psql -d hellozenno_development -P pager=off -A -t -c "SELECT * FROM table;"

# Backup local database
./scripts/local/backup_db.sh
```


## Common Commands

### Development
```bash
# Run Flask server - the user will always have this running in another terminal
source .env.local && ./scripts/local/run_backend.sh

# Run SvelteKit development server - the user will always have this running in another terminal
source .env.local && ./scripts/local/run_frontend.sh


### Deployment

see `scripts/`

```bash
# Deploy to production - the user should always be the one to do this
./scripts/prod/deploy.sh

# Backup production database - the user should always be the one to do this
./scripts/prod/backup_db.sh
```
