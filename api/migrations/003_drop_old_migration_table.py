"""Drop the old migration table if it exists."""

from peewee import PostgresqlDatabase


def migrate(migrator, database, *, fake=False):
    """Drop the old migration table if it exists."""
    if fake:
        return

    # Check if the table exists - different query for SQLite vs PostgreSQL
    if isinstance(database, PostgresqlDatabase):
        cursor = database.execute_sql(
            "SELECT tablename FROM pg_tables WHERE tablename = 'migration';"
        )
    else:
        cursor = database.execute_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migration';"
        )

    if cursor.fetchone():
        print("Found old migration table, dropping it...")
        migrator.sql("DROP TABLE migration;")
    else:
        print("Old migration table not found, skipping...")


def rollback(migrator, database, *, fake=False):
    """No rollback needed as we're removing an obsolete table."""
    pass
