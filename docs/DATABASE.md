This document describes the database setup and management scripts for the application.

see also:
- MIGRATIONS.md
- 

## Environment Tiers

The application uses PostgreSQL in all environments:

1. **Production** (Fly.io): PostgreSQL via internal network
   - Detected via `FLY_APP_NAME` environment variable - see `env_config.is_fly_cloud()`
   - Uses credentials from `.env.fly_cloud`
   - Connects via internal network on Fly.io

2. **Local-to-Fly**: Local development connecting to Fly.io PostgreSQL via proxy
   - Activated by setting `USE_FLY_POSTGRES_FROM_LOCAL_PROXY=1` - see `env_config.py`
   - Uses credentials from `.env.local_with_fly_proxy`
   - Connects via local proxy on port 15432

3. **Local Development**: Local PostgreSQL database
   - Default when no special environment variables are set
   - Uses credentials from `.env.local`
   - Database name defaults to "hellozenno_development"

## Database Scripts

Located in `scripts/database/`:

- `initialise_or_wipe_local_postgres.sh`: Sets up local PostgreSQL database
- `connect_to_fly_postgres_via_proxy.sh`: Establishes a proxy connection to the Fly.io production database
- `migrate_local.sh`: Runs migrations on local database
- `migrate_fly.sh`: Runs migrations on Fly.io database
- `migrate_fly_production_db_from_local_proxy.sh`: Runs migrations on production via proxy
- `backup_proxy_production_db.sh`: Creates a backup of the production database
- `migrations_list.sh`: Lists all available migrations

## Models

Main database models (`db_models.py`):

- `Lemma`: Dictionary form entries
- `Wordform`: Individual word forms
- `Sentence`: Example sentences
- `Phrase`: Multi-word expressions
- `Sourcedir`/`Sourcefile`: Source content management
- Various relationship models (e.g., `LemmaExampleSentence`, `SourcefileWordform`)

## Connection Management

The database connection (`db_connection.py`) features:

- Connection pooling
- Automatic environment detection
- Connection monitoring and logging
- Request-scoped connections in Flask
- Single source of truth for database configuration
- Used consistently across application (app, migrations, scripts)

## Testing

Test configuration (`conftest.py`) provides:

- Session-scoped test database
- Fast table cleanup between tests
- Test fixtures for database models
- Isolated test environments

## Usage

### Initial Setup

```bash
# Set up local development database
./scripts/database/initialise_or_wipe_local_postgres.sh
```

### Connecting to Production Database

```bash
# Via proxy from local machine
./scripts/database/connect_to_fly_postgres_via_proxy.sh

# Backup production database (requires proxy to be running)
# First start the proxy in a separate terminal:
./scripts/database/connect_to_fly_postgres_via_proxy.sh
# Then in another terminal:
./scripts/database/backup_proxy_production_db.sh
```

### Running Migrations

Don't ever make changes directly to the database, only as part of a migration (to keep local and Production in sync).

```bash
# Local development
./scripts/database/migrate_local.sh

# Production
./scripts/database/migrate_fly.sh
```

### Querying the local development database

See `config.py` and `db_connection.py` for the details of this.

Database credentials are stored in environment files:
- `.env.local` for local development
- `.env.local_with_fly_proxy` for connecting to production via proxy
- `.env.testing` for test environment
- `.env.fly_cloud` for production

Make sure to turn off pager mode (see below) so that you can see the output of running psql commands.

To connect to the local development database with nice formatting:

```bash
# Connect with expanded auto formatting and no pager
psql -d hellozenno_development -P pager=off -x auto

# Or for one-off queries, use these flags:
psql -d hellozenno_development -P pager=off -A -t -c "SELECT * FROM table;"
```

Common psql flags for better output:
- `-P pager=off`: Disable the pager (no more 'press space to continue')
- `-x auto`: Automatically switch between normal and expanded display
- `-A`: Unaligned output (good for copying data)
- `-t`: Print rows only (no headers/footers)
- `-q`: Quiet mode (no output except rows)

For JSON fields, cast to text for better readability:
```sql
SELECT id, metadata::text FROM sourcefile WHERE id = 7;
```
