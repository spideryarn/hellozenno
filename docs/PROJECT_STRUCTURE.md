# Project Structure

Overview of HelloZenno's directory structure and data flow architecture.

## Directory Structure

```
hellozenno/
├── backend/                 # Flask API backend
│   ├── api/
│   │   └── index.py        # Main Flask application entry
│   ├── views/              # API route handlers
│   ├── utils/              # Helper functions and utilities
│   ├── migrations/         # Database migration files
│   ├── db_models.py        # Peewee ORM models
│   ├── tests/              # Backend tests and mocks
│   └── docs/               # Backend documentation
│
├── frontend/               # SvelteKit frontend
│   ├── src/
│   │   ├── routes/        # SvelteKit pages and API routes
│   │   ├── lib/
│   │   │   ├── components/    # Reusable Svelte components
│   │   │   ├── generated/     # Auto-generated TypeScript files
│   │   │   ├── api.ts         # API client functions
│   │   │   └── stores/        # Svelte stores for state
│   │   └── app.html           # HTML template
│   ├── static/            # Static assets and CSS
│   └── docs/              # Frontend documentation
│
├── scripts/               # Automation scripts
│   ├── local/            # Local development scripts
│   └── prod/             # Production deployment scripts
│
├── docs/                  # Project-level documentation
│   ├── instructions/     # AI agent modes and workflows
│   ├── planning/         # Planning and decision docs
│   │   ├── finished/     # Completed implementations
│   │   └── obsolete/     # Abandoned plans
│   └── marketing/        # Marketing materials
│
├── gjdutils/             # Utility library (submodule)
├── logs/                 # Application logs
└── .env files            # Environment configuration
```

## Data Flow Architecture

```
User Browser
     ↓
SvelteKit Frontend (:5173)
     ↓
Flask API Backend (:3000)
     ↓
Supabase PostgreSQL
     +
Supabase Auth (JWT)
```

### Request Flow

1. **Frontend Request**: User action triggers SvelteKit route or component
2. **API Call**: Frontend uses `apiFetch()` with type-safe route names
3. **Authentication**: JWT token validated by Flask decorators
4. **Database Query**: Peewee ORM interacts with PostgreSQL
5. **Response**: JSON data returned through type-safe interfaces

### Key Integration Points

- **Route Generation**: Flask generates TypeScript types for frontend
- **Authentication**: Supabase JWT tokens validated on both sides
- **Type Safety**: Shared types between frontend and backend via generated files
- **Environment Config**: Consistent `.env` variables across stack

## Core Components

### Backend (Flask)
- **Entry**: `backend/api/index.py`
- **Routes**: `backend/views/*.py` 
- **Models**: `backend/db_models.py`
- **Auth**: `backend/utils/auth_utils.py`
- **Migrations**: `backend/migrations/*.py`

### Frontend (SvelteKit)
- **Pages**: `frontend/src/routes/`
- **Components**: `frontend/src/lib/components/`
- **API Client**: `frontend/src/lib/api.ts`
- **Stores**: `frontend/src/lib/stores/`
- **Types**: `frontend/src/lib/generated/routes.ts`

### Configuration
- **Local Dev**: `.env.local`
- **Testing**: `.env.testing`
- **Production**: `.env.prod`
- **Database**: `DATABASE_URL` in environment

### Scripts
- **Run Backend**: `./scripts/local/run_backend.sh`
- **Run Frontend**: `./scripts/local/run_frontend.sh`
- **Migrations**: `./scripts/local/migrate.sh`
- **Deploy**: `./scripts/prod/deploy.sh`

## Development Workflow

1. **Start Services**: Docker → Supabase → Backend → Frontend
2. **Make Changes**: Edit code with hot reload
3. **Type Check**: `npm run check` in frontend
4. **Test**: Run tests (when available)
5. **Deploy**: Use production scripts

See [backend/docs/DEVOPS.md](../backend/docs/DEVOPS.md) for detailed setup instructions.