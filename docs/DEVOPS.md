# Infrastructure & Development Guide

see also: planning/, e.g. DATABASE.md, MIGRATIONS.md

## Common Operations

### Testing
```bash
pytest  # Run all tests
pytest test_file.py  # Single file
pytest -k test_name  # Single test
```

### Deployment
```bash
./scripts/prod/deploy.sh  # Deploy to Fly.io
./scripts/health-checks/check.sh  # Run health checks manually
```
Includes database migrations and health checks

### Database Setup
```bash
./scripts/local/init_db.sh  # Set up local PostgreSQL database
```

### Database Migrations
- Create: `python utils/migrate.py create migration_name`
- Run locally: `./scripts/local/migrate.sh`
- List migrations: `./scripts/local/migrations_list.sh`
- Production: Handled by deploy.sh via `./scripts/prod/migrate.sh`

### Database Access
- Production database (Supabase):
  - Direct connection using DATABASE_URL from .env.prod
  - Uses transaction pooling on port 6543
  - Monitor via Supabase dashboard
  - Automatic backups handled by Supabase

For local development with production database:
- Copy `.env.local_to_prod.example` to `.env.local_to_prod`
- Update DATABASE_URL with your Supabase credentials
- Set environment variable: `export USE_LOCAL_TO_PROD=1`
- Your script can now use utils/db_connection.py to connect to production
- Remember to unset when done: `unset USE_LOCAL_TO_PROD`

### Monitoring
- Web app: `fly status -a hz-app-web`
- Database: Monitor via Supabase dashboard
- Web app logs: `fly logs --no-tail` (so it doesn't continually stream)
- Database logs: Available in Supabase dashboard

### Logging
- Flask app logs: `logs/flask_app.log` (limited to 100 lines via LimitingFileWriter)
- Vite dev server logs: `logs/vite_dev.log` (limited to 200 lines)
- Log configuration: See `utils/logging_utils.py` for Flask logging setup
- Frontend log capture: Configured in `scripts/local/run_frontend_dev.sh`

## Resource Management

### Web App Memory (fly.toml)
```toml
[[vm]]
  memory_mb = 768  # Edit this value
```
Takes effect on next deploy

### Database Resources
Managed through Supabase dashboard:
- Connection pooling
- Compute resources
- Storage
- Backups
- Monitoring

## Local Development

### Setup
1. Copy `.env.example` to `.env.local` and fill in your credentials
2. Install dev requirements: `pip install -r requirements-dev.txt`
3. Make scripts executable: `chmod +x scripts/**/*.sh`
4. Set up local database: `./scripts/local/init_db.sh`

### Configuration
- Environment variables: See `.env.example` for required variables
- Database: See `config.py` for connection settings
- Add language: Add to `SUPPORTED_LANGUAGES` in `config.py`
- Environment tiers: See `utils/db_connection.py` (Production, Local-to-Prod, Local Development)
- App settings: See `config.py` for file limits, language settings, etc. 