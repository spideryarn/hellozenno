"""Migration to drop the lemma_words column from Sentence table."""

from peewee import CharField, TextField, ForeignKeyField, Model
from playhouse.postgres_ext import JSONField

from db_models import BaseModel, Lemma, Sentence


def migrate(migrator, database, fake=False, **kwargs):
    """Drop the lemma_words column now that data is in junction table."""

    # Add new column
    migrator.sql("ALTER TABLE sentence ADD COLUMN lemma_words_new JSONB;")

    # Copy data
    migrator.sql("UPDATE sentence SET lemma_words_new = lemma_words;")

    # Drop old column
    migrator.sql("ALTER TABLE sentence DROP COLUMN lemma_words;")

    # Rename new column
    migrator.sql("ALTER TABLE sentence RENAME COLUMN lemma_words_new TO lemma_words;")


def rollback(migrator, database, fake=False, **kwargs):
    """Rollback the changes."""

    # Add new column
    migrator.sql(
        "ALTER TABLE sentence ADD COLUMN lemma_words_old JSONB NOT NULL DEFAULT '[]'::jsonb;"
    )

    # Copy data
    migrator.sql("UPDATE sentence SET lemma_words_old = lemma_words;")

    # Drop old column
    migrator.sql("ALTER TABLE sentence DROP COLUMN lemma_words;")

    # Rename new column
    migrator.sql("ALTER TABLE sentence RENAME COLUMN lemma_words_old TO lemma_words;")
