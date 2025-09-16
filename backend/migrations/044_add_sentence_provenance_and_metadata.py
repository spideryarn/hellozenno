"""Add provenance and generation_metadata to Sentence.

Follows backend/docs/MIGRATIONS.md patterns.
"""

import peewee as pw
from playhouse.postgres_ext import JSONField


def migrate(migrator, database, **kwargs):
    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    # Add fields (nullable JSON, provenance with default)
    with database.atomic():
        migrator.add_fields(
            Sentence,
            provenance=pw.CharField(default="manual"),
            generation_metadata=JSONField(null=True),
        )


def rollback(migrator, database, **kwargs):
    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    with database.atomic():
        migrator.drop_columns(Sentence, ["provenance", "generation_metadata"])
