# Database Migrations Guide

This guide documents our best practices and lessons learned for managing database migrations.

We're using the `peewee-migrate` library. I think it's this one:

https://github.com/klen/peewee_migrate/blob/develop/peewee_migrate/models.py#L21

and that it writes to the `migratehistory` table.

See also: DATABASE.md

## Core Principles

1. **Safety First**
   - Never drop tables unless explicitly requested
   - Never run migrations on production unless explicitly requested
   - Always wrap the entire migration in a `database.atomic()` transaction (so it either passes or fails in its entirety)
   - Try to write rollback functions, or if that's going to be very complicated then ask the user
   - Check with the user that they've backed up the database first - see scripts/prod/backup_db.sh
   
2. **Environment Management**
   - Environment detection is handled by `utils/db_connection.py`
   - Production is detected via `VERCEL` environment variable
   - Local-to-production mode via `USE_LOCAL_TO_PROD=1`
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

## Creating and Running Migrations

N.B. Don't run things on production without being explicitly asked to.

1. **Creating a Migration**
   ```bash
   # Change to the backend directory first
   cd backend
   
   # Create a new migration file with the proper template
   python -m utils.migrate create your_migration_name
   ```
   This will generate a numbered migration file like `NNN_your_migration_name.py` with the proper template.

2. **Local Development**
   ```bash
   # Run migrations locally
   ./scripts/local/migrate.sh
   ```

3. **Production**
   ```bash
   # Run migrations in production (handled by deploy.sh)
   ./scripts/prod/migrate.sh
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
   - Use the `utils/migrate.py` wrapper (from the backend directory) or `scripts/local/migrate.sh` for running migrations

2. **Naming and Organization**
   - Use descriptive migration names
   - Use `utils/migrate.py` (from the backend directory), which will generate sequential number prefixes, e.g., `001_initial_schema.py` for you
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
   - Avoid redundant index creation: If you define a field with `unique=True` in a model definition, Peewee automatically creates a unique index for that field during `create_model(Model)`. Don't call `add_index(Model, 'field_name', unique=True)` after that or you'll get a "relation already exists" error.

See `migrations/004_fix_sourcedir_language.py`, `migrations/029_add_profile_table.py`, and `migrations/032_add_various_fields.py` for examples.

## Adding Fields

When adding fields to existing table

1. Define model classes within the migration for each table you're modifying:
   ```python
   class Lemma(pw.Model):
       language_level = pw.CharField(null=True)
       created_by = pw.CharField(null=True)
       
       class Meta:
           table_name = 'lemma'
   ```

2. Pass the model class to `add_fields` instead of just the table name:
   ```python
   with database.atomic():
       migrator.add_fields(Lemma, 
           language_level=pw.CharField(null=True),
           created_by=pw.CharField(null=True),
       )
   ```

3. Define similar model classes in the rollback function (without field definitions):
   ```python
   class Lemma(pw.Model):
       class Meta:
           table_name = 'lemma'
   ```

## Cross-Schema Foreign Keys (e.g., to auth.users)

When creating foreign keys to tables in another schema (such as Supabase's `auth.users`), we use one of two approaches:

### Approach 1: Define fields as UUIDs and add FK constraints with SQL (Preferred)

This is our preferred approach for references to `auth.users`:

1. Define an unmanaged model for the foreign table in the migration (only for reference):
   ```python
   class AuthUser(pw.Model):
       id = pw.UUIDField(primary_key=True)
       
       class Meta:
           table_name = 'users'
           schema = 'auth'
   ```

2. Add the field as a simple UUIDField:
   ```python
   class YourModel(pw.Model):
       created_by_id = pw.UUIDField(null=True)  # Use _id suffix by convention
       
       class Meta:
           table_name = 'your_table'
   
   migrator.add_fields(
       YourModel,
       created_by_id=pw.UUIDField(null=True), 
   )
   ```

3. Add the foreign key constraint explicitly using SQL:
   ```python
   migrator.sql(
       """
       ALTER TABLE "your_table" 
       ADD CONSTRAINT fk_your_table_created_by_id
       FOREIGN KEY ("created_by_id")
       REFERENCES "auth"."users" ("id") 
       ON DELETE CASCADE;
       """
   )
   ```

4. In your model definition in `db_models.py`, use UUIDField as well:
   ```python
   class YourModel(BaseModel):
       created_by_id = UUIDField(null=True)  # Not a ForeignKeyField
   ```

See `migrations/033_add_user_reference_fields.py` and `migrations/034_add_userlemma_table.py` for complete examples.

### Approach 2: Use ForeignKeyField with cross-schema reference

1. Define an unmanaged model for the foreign table with the correct schema:
   ```python
   class AuthUser(pw.Model):
       id = pw.UUIDField(primary_key=True)
       
       class Meta:
           database = database
           table_name = 'users'
           schema = 'auth'    # Specify the schema
           managed = False    # Don't modify this table
   ```

2. Use this model as the target for your ForeignKeyField:
   ```python
   class YourModel(pw.Model):
       class Meta:
           table_name = 'your_table'
   
   migrator.add_fields(
       YourModel,
       created_by=pw.ForeignKeyField(
           AuthUser,              # Reference the auth schema model
           field='id',            # Field in auth.users to reference
           backref='your_models', # Back reference name
           null=True,             # Allow NULL values 
           on_delete='CASCADE'    # CASCADE on delete
       )
   )
   ```

3. Peewee will handle the cross-schema reference, but you may need to add explicit constraints


## Questions or Improvements?

- If you see problems or a better way, discuss before proceeding
- If you get stuck, stop and review, ask for help
- Update this guide if you discover new patterns or best practices
- Always ask if you have questions!
