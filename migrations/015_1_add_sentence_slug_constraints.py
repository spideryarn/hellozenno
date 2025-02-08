"""Add constraints to sentence slug field."""

from peewee import CharField, Model
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database, *, fake=False):
    """Add NOT NULL constraint and unique index to slug field."""

    # Make slug required
    migrator.sql("ALTER TABLE sentence ALTER COLUMN slug SET NOT NULL")

    # Add unique index
    migrator.sql(
        "CREATE UNIQUE INDEX sentence_slug_language_code_idx ON sentence (slug, language_code)"
    )


def rollback(migrator: Migrator, database, *, fake=False):
    """Remove constraints from slug field."""

    # Drop the index first
    migrator.sql("DROP INDEX IF EXISTS sentence_slug_language_code_idx")

    # Then make the column nullable again
    migrator.sql("ALTER TABLE sentence ALTER COLUMN slug DROP NOT NULL")
