# Database Migrations Guide

This guide documents our best practices and lessons learned for managing database migrations.

See also: DATABASE.md

## Core Principles

1. **Safety First**
   - Never drop tables unless explicitly requested
   - Never run migrations on production unless explicitly requested
   - Always wrap migrations in `database.atomic()` transactions
   - Try to write rollback functions, or if that's going to be very complicated then ask the user
   - Check with the user that they've backed up the database first - see backup_proxy_production_db.sh
   
2. **Environment Management**
   - Environment detection is handled by `utils/db_connection.py`
   - Production (Fly.io) is detected via `FLY_APP_NAME` environment variable
   - Local-to-Fly proxy mode via `USE_FLY_POSTGRES_FROM_LOCAL_PROXY=1`
   - Local development is the default when no special variables are set
   - All database configuration is centralized in `utils/db_connection.py`

3. **Checking locally**
   - Make sure to run migrations locally before deploying to production
   - After running a migration locally, inspect the state of the database to make sure it looks as expected
   - Run all the tests

4. **PostgreSQL Features**
   - Use PostgreSQL-specific features when they provide clear benefits
   - Prefer Peewee's built-in functions over raw SQL whenever possible
   - When raw SQL is needed, use `migrator.sql()` rather than `database.execute_sql()`
   - Take advantage of PostgreSQL's JSONB fields, array types, and other advanced features

## Running Migrations

N.B. Don't run things on production without being explicitly asked to.

1. **Local Development**
   ```bash
   ./scripts/database/migrate_local.sh
   ```

2. **Production (Fly.io)**

    (This should get run as part of the standar )
   ```bash
   # First backup the database
   ./scripts/database/backup_proxy_production_db.sh
   
   # Then run migrations
   ./scripts/database/migrate_fly.sh
   ```

3. **Production via Proxy** (if needed)
   ```bash
   # Start proxy in another terminal
   ./scripts/database/connect_to_fly_postgres_via_proxy.sh
   
   # Run migrations with dry-run first
   ./scripts/database/migrate_fly_production_db_from_local_proxy.sh --dry-run
   
   # Then run for real if dry-run looks good
   ./scripts/database/migrate_fly_production_db_from_local_proxy.sh
   ```

## Common Patterns

### Adding Required Columns

Three-step process to avoid nulls (see `migrations/004_fix_sourcedir_language.py`):
1. Add column as nullable with a default value
   ```python
   migrator.add_columns(
       Model,
       new_field=CharField(max_length=2, default="el"),
   )
   ```
2. Fill existing rows
   ```python
   migrator.sql("UPDATE table SET new_field = 'value'")
   ```
3. Make it required and remove default
   ```python
   migrator.sql("ALTER TABLE table ALTER COLUMN new_field SET NOT NULL")
   migrator.sql("ALTER TABLE table ALTER COLUMN new_field DROP DEFAULT")
   ```

Note: For complex operations or when using Python functions (like `slugify`), consider:
- Prefer to use Peewee's built-in functions when possible (e.g., `migrator.add_columns()`, `migrator.drop_columns()`)
- For raw SQL operations, always use `migrator.sql()` rather than `database.execute_sql()`
- Separating steps into individual transactions with `database.atomic()`
- Using parameterized queries for safety with `migrator.sql("UPDATE ... WHERE id = %s", (value,))`

### Managing Indexes

1. Drop existing index if needed:
   ```python
   migrator.sql('DROP INDEX IF EXISTS "index_name";')
   ```

2. Create new index:
   ```python
   migrator.sql(
       'CREATE UNIQUE INDEX new_index_name ON table (column1, column2);'
   )
   ```

See `migrations/004_fix_sourcedir_language.py` for an example.

### Model Definitions in Migrations

When using `add_columns` or `drop_columns`, you need to define model classes in both `migrate` and `rollback` functions:

```python
class BaseModel(Model):
    created_at = DateTimeField()
    updated_at = DateTimeField()

class MyModel(BaseModel):
    field = CharField()

    class Meta:
        table_name = "my_table"

# Then use the model class, not string name:
migrator.drop_columns(MyModel, ["field"])
```

Note: No need to bind models to database - they're just used for schema definition.

## Best Practices

1. **Model Updates**
   - Always update `db_models.py` to match migration changes
   - Keep model and migration in sync
   - Add appropriate type hints and docstrings
   - Make a proposal for which indexes (informed by how we're querying that model) we'll need, but check with the user first
   - Wherever possible, use Peewee's built-in migration functions (e.g., `migrator.add_columns()`, `migrator.drop_columns()`)
   - When raw SQL is unavoidable, always use `migrator.sql()` - never use `database.execute_sql()`
   - Use the `utils/migrate.py` wrapper or `migrate_local.sh` for running migrations

2. **Naming and Organization**
   - Use descriptive migration names
   - Use `utils/migrate.py`, which will should generate sequential number prefixes, e.g., `001_initial_schema.py` for you
   - One logical change per migration

3. **Error Handling**
   - Use `database.atomic()` for transactions
   - Handle database-specific errors
   - Provide clear error messages

4. **Documentation**
   - Document complex migrations
   - Note any manual steps required
   - Update this guide with new learnings

5. **Common Mistakes to Avoid**
   - Use `add_columns` not `add_column`
   - Use `drop_columns(['column_name'])` not `drop_column`
   - Define model classes in both `migrate` and `rollback` functions if you need to use them
   - Don't make assumptions about existing data
   - Always test migrations on a copy of production data before deploying

See `migrations/004_fix_sourcedir_language.py` for an example.

## Questions or Improvements?

- If you see problems or a better way, discuss before proceeding
- If you get stuck, stop and review, ask for help
- Update this guide if you discover new patterns or best practices
- Always ask if you have questions!
