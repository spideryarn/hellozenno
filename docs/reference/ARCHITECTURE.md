# Architecture

Hello Zenno uses a hybrid architecture: SvelteKit frontend and Flask backend API, with Supabase (PostgreSQL + Auth).

## Overview

- Frontend: SvelteKit app in `frontend/`
  - Renders UI, calls the Flask API via `apiFetch`
  - Type-safe API bindings generated to `frontend/src/lib/generated/`
  - Auth handled with Supabase (`@supabase/ssr`)
- Backend: Flask app in `backend/`
  - Entrypoint `backend/api/index.py`
  - Routes in `backend/views/*_api.py` (JSON), `*_views.py` (legacy HTML)
  - Peewee ORM models in `backend/db_models.py`
- Database: Supabase Postgres
  - Migrations in `backend/migrations/`
  - Connection via transaction pooler (port 6543)

## Data Flow

1. SvelteKit pages load server-side where appropriate, creating a server Supabase client.
2. API requests are made through `apiFetch` which attaches `Authorization: Bearer <token>` when available.
3. Flask endpoints validate tokens (`@api_auth_required` or `@api_auth_optional`) and access Peewee models.
4. Responses are returned as JSON; frontend renders components and tooltips (e.g., EnhancedText) accordingly.

## Key Docs

- Frontend architecture: `../../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`
- API integration: `../../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md`
- Authentication: `../../frontend/docs/AUTH.md`
- Database: `../../backend/docs/DATABASE.md`, `../../backend/docs/MODELS.md`
- URL registry and type generation: `../../backend/docs/URL_REGISTRY.md`

## Deployment

- Backend and frontend are deployed on Vercel as separate projects (API and frontend)
- Supabase provides managed Postgres and Auth
- See `../../backend/docs/DEVOPS.md` for environment and deployment scripts
- Vercel function timeout defaults to ~30s; long-running generation should be queued or pre-warmed

### Rationale for the hybrid approach

- Keep server-rendered SvelteKit UX for speed and SEO while centralizing domain logic in Flask
- Type-safe boundary via generated routes provides refactor safety and shared contracts
- Supabase handles identity and Postgres so the app focuses on product logic
