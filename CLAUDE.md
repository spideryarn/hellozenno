# HelloZenno Project Reference

To understand more about the purpose of the app, see `./README.md`

## Coding

- Make sure you read `.cursor/rules/gjdutils_rules/coding.mdc`

- **Backend (Flask + PostgreSQL)**
  - `app.py` - Main Flask application
  - `views/` - Route handlers and view functions
  - `utils/` - Helper functions
  - `db_models.py` - Database models (using Peewee ORM)
  - `migrations/` - Database migration scripts

- **Frontend (Svelte + TypeScript + Vite)**
  - Read `FRONTEND_INFRASTRUCTURE.md` before creating new frontend components
  - Use the `browser-tools` MCP to read the browser console logs, get screenshots, etc
  - folder structure:
    - `frontend/src/components/` - Svelte components
    - `frontend/src/entries/` - Entry points for different pages
    - `frontend/src/lib/` - Shared utilities
    - `templates/` - Jinja templates
    - `static/` - Static assets

## Development Guidelines

### Database
- see `DATABASE.md`, and also use the Supabase MCP (read-only)
- see `MIGRATIONS.md` before creating or running migrations

### Frontend Components

### Testing

see `.cursor/rules/gjdutils_rules/testing.mdc` and `docs/TESTING.md`

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/backend/test_file.py
pytest -k test_name
pytest -x --lf # Stop on first failure, then run last failed

# Run with verbose output
pytest -v
```

### Database
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
source .env.local && ./scripts/local/run_flask.sh

# Run frontend development server (Vite) - the user will always have this running in another terminal
source .env.local && ./scripts/local/run_frontend_dev.sh

# Database migrations
./scripts/local/migrations_list.sh # List available migrations
./scripts/local/migrate.sh
```

### Deployment

see `scripts/`

```bash
# Deploy to production
./scripts/prod/deploy.sh

# Backup production database
./scripts/prod/backup_db.sh
```
