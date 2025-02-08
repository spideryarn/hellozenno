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
./scripts/fly/deploy.sh  # Deploy to Fly.io
./scripts/health-checks/check.sh  # Run health checks manually
```
Includes database migrations and health checks

### Database Setup
```bash
./scripts/database/initialise_or_wipe_local_postgres.sh  # Set up local PostgreSQL database
```

### Database Migrations
- Create: `python migrate.py create migration_name`
- Run locally: `./scripts/database/migrate_local.sh`
- List migrations: `./scripts/database/migrations_list.sh`
- Production: Handled by deploy.sh via `./scripts/database/migrate_fly.sh`

### Database Access
- Connect to production: `./scripts/database/connect_to_fly_postgres_via_proxy.sh`
  - Sets up a secure proxy tunnel to Fly.io Postgres on port 15432
  - Connects via psql using credentials from _secrets.py
  - Automatically cleans up when you exit psql
  - If port 15432 is in use, either wait or kill existing proxy (script will guide you)

For scripts that need to connect to production database from local:
- First run `./scripts/database/connect_to_fly_postgres_via_proxy.sh` to start the proxy
- Set environment variable: `export USE_FLY_POSTGRES_FROM_LOCAL_PROXY=1`
- Your script can now use db_connection.py which will automatically connect via the proxy
- The proxy must remain running while your script executes
- Remember to unset when done: `unset USE_FLY_POSTGRES_FROM_LOCAL_PROXY`

### Monitoring
- Web app: `fly status -a hz-app-web`
- Database: `fly status -a hz-app-db-prod`
- Logs: `fly logs`

## Resource Management

### Web App Memory (fly.toml)
```toml
[[vm]]
  memory_mb = 768  # Edit this value
```
Takes effect on next deploy

### Database Memory
```bash
fly machine list -a hz-app-db-prod  # Get machine ID
fly machine update MACHINE_ID --memory 512 -a hz-app-db-prod -y
```
Takes effect immediately

## Local Development

### Setup
1. Get `_secrets.py` from Greg (not in repo)
2. Install dev requirements: `pip install -r requirements-dev.txt`
3. Make scripts executable: `chmod +x scripts/**/*.sh`
4. Set up local database: `./scripts/database/initialise_or_wipe_local_postgres.sh`

### Configuration
- Database: See `config.py` for connection settings
- Add language: Add to `SUPPORTED_LANGUAGES` in `config.py`
- Environment tiers: See `db_connection.py` (Fly.io, Local-to-Fly, Local Development)
- App settings: See `config.py` for file limits, language settings, etc. 