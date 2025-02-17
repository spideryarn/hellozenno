This document describes the database setup and management scripts for the application.

see also:
- MIGRATIONS.md

## Environment Tiers

The application uses PostgreSQL (via Supabase) in all environments:

1. **Production**: Supabase PostgreSQL
   - Uses connection string from `.env.prod`
   - Connects directly to Supabase over HTTPS
   - Uses transaction pooling (port 6543) for optimal performance
   - SSL mode required for security

2. **Local Development**: Local PostgreSQL database
   - Default when no special environment variables are set
   - Uses connection string from `.env.local`
   - Database name defaults to "hellozenno_development"

3. **Local-to-Production**: Direct connection to Supabase for debugging
   - Uses connection string from `.env.local_to_prod`
   - Connects directly to Supabase (no proxy needed)
   - Useful for debugging production database issues
   - Use with caution - read-only operations recommended

4. **Testing**: Local PostgreSQL test database
   - Uses connection string from `.env.testing`
   - Isolated test database with name ending in "_test"
   - Automatically managed by test suite

## Database Scripts

Located in `scripts/prod/` and `scripts/local/`:

- `scripts/local/init_db.sh`: Sets up local PostgreSQL database
- `scripts/local/migrate.sh`: Runs migrations on local database
- `scripts/prod/migrate.sh`: Runs migrations on production database
- `scripts/local/backup_db.sh`: Creates a backup of the local database
- `scripts/local/migrations_list.sh`: Lists all available migrations

N.B. We used to host our Postgres database on Fly.io, but now we use Supabase for that. If you see references to Fly.io and databases, please update them. See `planning/250216_Supabase_database_migration.md`

## Models

Main database models (`db_models.py`):

- `Lemma`: Dictionary form entries
- `Wordform`: Individual word forms
- `Sentence`: Example sentences
- `Phrase`: Multi-word expressions
- `Sourcedir`/`Sourcefile`: Source content management
- Various relationship models (e.g., `LemmaExampleSentence`, `SourcefileWordform`)

## Connection Management

The database connection (`utils/db_connection.py`) features:

- Connection pooling via Supabase's transaction pooler
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
# Initialize local database
./scripts/local/init_db.sh
```

### Connecting to Production Database

For debugging or maintenance tasks, you can connect directly to the production database:

- Use `.env.local_to_prod`:

- Connect using psql:
   ```bash
   # Using the connection string from .env.local_to_prod
   source .env.local_to_prod && psql "$DATABASE_URL"
   ```

- Or for specific operations:
   ```bash
   # Backup the production database
   ./scripts/prod/backup_db.sh

   # Run a specific query
   source .env.local_to_prod && psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM lemma;"
   ```

**Important Safety Notes:**
- Always use read-only operations unless you have a specific need to write
- Never run migrations this way - use `migrate_prod.sh` instead
- Consider using transaction blocks (`BEGIN; ... ROLLBACK;`) to prevent accidental changes
- Take a backup before any maintenance work
- Be cautious with large queries that might impact production performance

### Running Migrations

Don't ever make changes directly to the database, only as part of a migration (to keep local and Production in sync).

```bash
# Run migrations locally
./scripts/local/migrate.sh

# Run migrations in production
./scripts/prod/migrate.sh
```

### Querying the local development database

Database credentials are stored in environment files:
- `.env.local` for local development
- `.env.testing` for test environment
- `.env.prod` for production

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
