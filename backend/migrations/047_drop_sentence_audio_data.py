"""Drop legacy audio_data column from sentence."""

import peewee as pw
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database: pw.Database, **kwargs):
    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    with database.atomic():
        migrator.drop_columns(Sentence, ["audio_data"])


def rollback(migrator: Migrator, database: pw.Database, **kwargs):
    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    with database.atomic():
        migrator.sql("ALTER TABLE sentence ADD COLUMN audio_data BYTEA")
