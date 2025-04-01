"""Add is_complete field to Lemma to track metadata completeness."""

from peewee import (
    BooleanField,
    Model,
    CharField,
    TextField,
    FloatField,
    DateTimeField,
)


def migrate(migrator, database, *, fake=False):
    """Add is_complete field to Lemma."""
    if fake:
        return

    with database.atomic():
        # For PostgreSQL, we can use ALTER COLUMN
        database.execute_sql("ALTER TABLE lemma ADD COLUMN is_complete BOOLEAN;")
        database.execute_sql("UPDATE lemma SET is_complete = TRUE;")
        database.execute_sql("ALTER TABLE lemma ALTER COLUMN is_complete SET NOT NULL;")


def rollback(migrator, database, *, fake=False):
    """Rollback the migration."""
    if fake:
        return

    with database.atomic():
        migrator.drop_column("lemma", "is_complete")
