"""Peewee migrations -- 038_drop_difficulty_level_from_phrase.py.

This migration removes the `difficulty_level` field from the Phrase model as part of
standardizing on CEFR language levels (A1-C2) using the `language_level` field that was
added in migration 037_add_language_level_to_phrase.py.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove difficulty_level field from Phrase table."""
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Phrase(BaseModel):
        class Meta:
            table_name = "phrase"

    with database.atomic():
        # Remove the difficulty_level field from Phrase table
        migrator.remove_fields(Phrase, "difficulty_level")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add back the difficulty_level field to Phrase table."""
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Phrase(BaseModel):
        difficulty_level = pw.CharField(null=True)

        class Meta:
            table_name = "phrase"

    with database.atomic():
        # Add back the difficulty_level field to Phrase table
        migrator.add_fields(
            Phrase,
            difficulty_level=pw.CharField(null=True),
        )
