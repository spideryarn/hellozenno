This document describes the database setup and management scripts for the application.

see also:
- MIGRATIONS.md
- [MODELS.md](./MODELS.md) - Detailed overview of database models

## Environment Tiers

The application uses PostgreSQL (via Supabase) in all environments:

1. **Production**: Supabase PostgreSQL
   - Uses connection string from `.env.prod`
   - Connects via Supabase's session pooler (port 5432)
   - Supports all PostgreSQL features including prepared statements
   - SSL mode required for security
   - Optimized for long-lived containers with light traffic

2. **Local Development**: Local PostgreSQL database
   - Default when no special environment variables are set
   - Uses connection string from `.env.local`
   - Database name defaults to "postgres"

3. **Local-to-Production**: Direct connection to Supabase for debugging
   - Uses connection string from `.env.prod`
   - Connects directly to Supabase (no proxy needed)
   - Useful for debugging production database issues
   - Use with caution - read-only operations recommended

4. **Testing**: Local PostgreSQL test database
   - Uses connection string from `.env.testing`
   - Isolated test database with name ending in "_test"
   - Automatically managed by test suite

## Connection Options with Supabase

Supabase offers three main connection methods:

1. **Direct Connection**:
   - Connects directly to your Postgres instance
   - Uses IPv6 by default
   - Ideal for persistent servers with few connections
   - Connection string format: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

2. **Session Pooler**:
   - Connects via a proxy on port 5432
   - Ideal for persistent servers when IPv6 is not supported
   - Supports all PostgreSQL features including prepared statements
   - Good for applications with fewer clients that maintain long sessions

3. **Transaction Pooler** (preferred in production and serverless):
   - Connects via a proxy on port 6543
   - Ideal for serverless or edge functions with many transient connections
   - Does NOT support prepared statements
   - Better for high-concurrency scenarios with short-lived connections

## Database Scripts

Located in `scripts/prod/` and `scripts/local/`:

- `scripts/local/init_db.sh`: Sets up local PostgreSQL database
- `scripts/local/migrate.sh`: Runs migrations on local database
- `scripts/prod/migrate.sh`: Runs migrations on production database
- `scripts/local/backup_db.sh`: Creates a backup of the local database
- `scripts/local/migrations_list.sh`: Lists all available migrations

Note: We migrated from Fly.io-hosted Postgres to Supabase. Historical notes are in `docs/planning/finished/250216_Supabase_database_migration.md`. All current environments should use Supabase.

## Models

Main database models (`db_models.py`):

- `Lemma`: Dictionary form entries
- `Wordform`: Individual word forms
- `Sentence`: Example sentences
- `Phrase`: Multi-word expressions
- `Sourcedir`/`Sourcefile`: Source content management
- Various relationship models (e.g., `LemmaExampleSentence`, `SourcefileWordform`)
- `UserLemma`: Junction table linking `auth.users` directly to lemmas

See [MODELS.md](./MODELS.md) for a comprehensive overview of all models, their fields, and relationships.

### Schema verification

For documentation accuracy, periodically verify the public schema and align `MODELS.md` with reality. Preferred options:

- Using the Supabase_local MCP: run read-only queries against `information_schema` and `pg_constraint` to list tables, columns, PKs, FKs, uniques, and enums.
- Alternatively via psql:
  ```bash
  psql -d postgres -U postgres -h 127.0.0.1 -p 54322 -P pager=off -A -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY 1;"
  ```

Include notable differences in a docs update.

### Note on `profile` vs `profiles` tables

- Background: Supabase local setup sometimes includes a starter table `public.profiles` (UUID pk, FK to `auth.users`). Our application, however, intentionally manages its own `public.profile` table via Peewee migrations for app‑specific fields like `target_language_code` and `admin_granted_at`.
- Impact: Having both tables led to confusion when inspecting the schema and generated types. The app only reads/writes `public.profile`; `public.profiles` is unused.
- Resolution: We dropped `public.profiles` in migration `042_drop_supabase_profiles_table.py`. The canonical table is `public.profile` as defined in `backend/db_models.py` and created/evolved via our migrations (`029_add_profile_table.py`, `041_add_profile_admin_granted_at.py`).
- Guidance: If Supabase tooling re‑introduces `public.profiles` locally, re‑run migrations (`./scripts/local/migrate.sh`). Do not add code that references `public.profiles`.

### Linter Considerations

Static analysis tools (like Pyright, used by Pylance in VS Code) may sometimes report false positive errors when working with Peewee models, particularly concerning dynamically generated attributes like `id` or field access within join conditions (e.g., `Model.id`).

For example, you might see errors like "Cannot access attribute 'id' for class 'type[ModelName]*'". In many cases, if the Peewee code follows standard ORM patterns, these can be treated as linter misinterpretations due to Peewee's dynamic nature.

Consider adding a comment `#  type: ignore` at the end of the line to suppress them.

### Cross-Schema References

We're still evolving the best approach for this, but this is the current thinking.

Our models often reference Supabase's `auth.users` table. When working with such cross-schema references:

1. For model definitions (`db_models.py`), we define an `AuthUser` model with the appropriate schema:
   ```python
   class AuthUser(Model):
       """Model to reference Supabase auth.users table."""
       id = UUIDField(primary_key=True)
       
       class Meta:
           database = database
           table_name = "users"
           schema = "auth"
   ```

2. For referencing user IDs, we use a `UUIDField()` rather than `ForeignKeyField`:
   ```python
   class SomeModel(BaseModel):
       # Direct reference to auth.users.id
       user_id = UUIDField()  
   ```

3. For migrations, see the detailed section on cross-schema foreign keys in [MIGRATIONS.md](./MIGRATIONS.md).

## Connection Management

The database connection (`utils/db_connection.py`) features:

- Connection pooling via Supabase's transaction pooler (port 6543)
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

- Use `.env.prod`:

- Connect using psql:
   ```bash
   # Using the connection string from .env.prod
   source .env.prod && psql "$DATABASE_URL"
   ```

- Or for specific operations:
   ```bash
   # Backup the production database
   ./scripts/prod/backup_db.sh

   # Run a specific query
   source .env.prod && psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM lemma;"
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

**Tip**: by far the simplest way to connect to the local development database is to use the Supabase_local MCP if that is available.

Failing that, you can use the terminal... see below.

Database credentials are stored in environment files:
- `.env.local` for local development
- `.env.testing` for test environment
- `.env.prod` for production

Make sure to turn off pager mode (see below) so that you can see the output of running psql commands.

To connect to the local development database with nice formatting:

```bash
# Connect with expanded auto formatting and no pager
psql -d postgres -U postgres -h 127.0.0.1 -p 54322 -P pager=off -x auto

# Or for one-off queries, use these flags:
psql -d postgres -U postgres -h 127.0.0.1 -p 54322 -P pager=off -A -t -c "SELECT * FROM table;"
```

### Local auth users for E2E / admin testing

We intentionally use `public.profile` (singular) for app data. Supabase’s default `public.profiles` is not used and was removed. The `backend/oneoff/create_local_test_auth_users.sql` script will:

- Create two local auth users in `auth.users` with bcrypt passwords
- Create matching `auth.identities`
- Ensure `public.profile` rows exist and grant admin to `admin@hellozenno.com`
- Drop the default `auth.users` trigger (`on_auth_user_created`) that inserts into `public.profiles` to avoid conflicts

Run it locally:

```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -p 54322 -U postgres -d postgres -P pager=off -f backend/oneoff/create_local_test_auth_users.sql | cat
```

Resulting users (local only):

- testing@hellozenno.com / hello123
- admin@hellozenno.com / hello123 (admin)

## Useful tips

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
