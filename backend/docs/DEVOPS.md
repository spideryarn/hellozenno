# Infrastructure & Development Guide

This document provides an overview of the infrastructure, deployment processes, and development workflows for the Hello Zenno application.

## Architecture Overview

Hello Zenno uses a dual-architecture approach:

1. **Flask API Backend** - Located in `backend/api/index.py` and `backend/views/*_api.py`, deployed to `api.hellozenno.com`
2. **SvelteKit Frontend** - Located in `frontend/`, deployed to `www.hellozenno.com`

For more detailed information on the architecture:
- [SvelteKit Architecture](../../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)
- [Flask API Integration](../../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md)
- [Vercel Setup Plan](../../planning/250331_Vercel_setup_for_SvelteKit.md)
- See also: [Database Documentation](../../docs/DATABASE.md) and [Migrations Guide](../../docs/MIGRATIONS.md)

## Common Operations

### Local Development

#### Running the Backend
```bash
export FLASK_PORT=3000  # Required environment variable
./scripts/local/run_backend.sh
```

The Flask API runs on port 3000 and generates logs in `logs/backend.log`.

#### Running the Frontend
```bash
./scripts/local/run_frontend.sh
```

The SvelteKit frontend runs on port 5173 and generates logs in `logs/frontend.log`.

### Testing
```bash
pytest  # Run all tests
pytest test_file.py  # Single file
pytest -k test_name  # Single test
```

### Deployment

The project uses Vercel for deployment with separate projects for backend and frontend.

#### Full Deployment
```bash
./scripts/prod/deploy.sh  # Deploy both backend and frontend to production
./scripts/prod/deploy.sh --preview  # Deploy to preview environments
```

#### Component Deployment
```bash
./scripts/prod/deploy_backend.sh  # Deploy only the backend
./scripts/prod/deploy_frontend.sh  # Deploy only the frontend
```

Each deployment script includes health checks to verify successful deployment.

### Database Setup

```bash
./scripts/local/init_db.sh  # Set up local PostgreSQL database
```

### Database Migrations

- Create: `python utils/migrate.py create migration_name`
- Run locally: `./scripts/local/migrate.sh`
- List migrations: `./scripts/local/migrations_list.sh`
- Production: Handled by deploy.sh via `./scripts/prod/migrate.sh`

## Resource Management

### Vercel Resources

#### Frontend Project
Managed through Vercel dashboard (`hz_frontend` project):
- Serverless function configuration
- Environment variables
- Deployment settings
- Monitoring and logs

#### Backend API Project
Managed through Vercel dashboard (`hz_backend` project):
- Serverless function configuration
- Environment variables
- Deployment settings
- Monitoring and logs

### Database Resources
Managed through Supabase dashboard:
- Connection pooling
- Compute resources
- Storage
- Backups
- Monitoring

## Environment Configuration

### Local Development

1. Copy `.env.example` to `.env.local` and fill in your credentials
2. Install development requirements: `pip install -r requirements-dev.txt`
3. Make scripts executable: `chmod +x scripts/**/*.sh`
4. Set up local database: `./scripts/local/init_db.sh`
5. Install frontend dependencies: `cd frontend && npm install`

### Production Configuration

- Backend: Environment variables are set in `.env.prod` and deployed to Vercel
- Frontend: Environment variables including `VITE_API_URL` are set in `.env.prod` and deployed to Vercel

### Database Access

- Production database (Supabase):
  - Direct connection using DATABASE_URL from .env.prod
  - Uses transaction pooling on port 6543
  - Monitor via Supabase dashboard
  - Automatic backups handled by Supabase

For local development with production database:
- Use `.env.prod` which contains the production database credentials
- Set environment variable: `export USE_LOCAL_TO_PROD=1`
- Your script can now use utils/db_connection.py to connect to production
- Remember to unset when done: `unset USE_LOCAL_TO_PROD`

## Monitoring and Logging

### Monitoring
- Frontend: Monitor via Vercel dashboard for `hz_frontend` project
- Backend API: Monitor via Vercel dashboard for `hz_backend` project
- Database: Monitor via Supabase dashboard

### Logging
- Flask API logs: `logs/backend.log` (limited to 200 lines)
- SvelteKit dev server logs: `logs/frontend.log`
- Production logs: see DEBUGGING.md for the issues with `vercel logs --json`

## API Integration

The Flask API automatically generates TypeScript type definitions for all routes:
- Route definitions are stored in `frontend/src/lib/generated/routes.ts`
- SvelteKit components use these definitions for type-safe API calls

For more details on API integration, see [Flask API Integration](../../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md). 