"""Add SourcefilePhrase table.

Creates a new table to link phrases to sourcefiles, with metadata about the phrase's
importance and display order in the sourcefile context.
"""

from peewee import (
    Model,
    ForeignKeyField,
    FloatField,
    IntegerField,
    DateTimeField,
)
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database, **kwargs):
    """Create SourcefilePhrase table."""

    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcefile(BaseModel):
        class Meta:
            table_name = "sourcefile"

    class Phrase(BaseModel):
        class Meta:
            table_name = "phrase"

    class SourcefilePhrase(BaseModel):
        sourcefile = ForeignKeyField(Sourcefile)
        phrase = ForeignKeyField(Phrase)
        centrality = FloatField(
            null=True
        )  # from 0-1 indicating importance of phrase in the sourcefile
        ordering = IntegerField(null=True)  # display order in the sourcefile

        class Meta:
            table_name = "sourcefilephrase"

    with database.atomic():
        # Create the table
        migrator.create_model(SourcefilePhrase)

        # Add unique index on sourcefile and phrase
        migrator.sql(
            'CREATE UNIQUE INDEX "sourcefilephrase_sourcefile_phrase" ON sourcefilephrase (sourcefile_id, phrase_id);'
        )


def rollback(migrator: Migrator, database, **kwargs):
    """Remove SourcefilePhrase table."""
    with database.atomic():
        # Drop the table
        migrator.drop_table("sourcefilephrase")
