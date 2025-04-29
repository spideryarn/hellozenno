"""Peewee migrations -- 037_add_language_level_to_phrase.py.

This migration adds the `language_level` field to the Phrase model. This field
was defined in the Phrase model class but was missing from the database table.

The field is nullable to maintain backward compatibility with existing data.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add language_level field to Phrase table."""
    # Define models with the fields we want to add
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Phrase(BaseModel):
        language_level = pw.CharField(null=True)

        class Meta:
            table_name = "phrase"

    with database.atomic():
        # Add language_level to Phrase table
        migrator.add_fields(
            Phrase,
            language_level=pw.CharField(null=True),
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove the language_level field from Phrase table."""
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Phrase(BaseModel):
        class Meta:
            table_name = "phrase"

    # Remove field from Phrase
    with database.atomic():
        migrator.remove_fields(Phrase, "language_level")
