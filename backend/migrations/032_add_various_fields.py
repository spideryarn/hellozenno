"""Peewee migrations -- 032_add_various_fields.py.

This migration adds fields that reference the Supabase auth.users table:
- publication_date, num_words, language_level, url, title_target to Sourcefile
- language_level to Lemma and Sentence

All fields are nullable to maintain backward compatibility with existing data.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    # Define models with the fields we want to add
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Lemma(BaseModel):
        language_level = pw.CharField(null=True)

        class Meta:
            table_name = "lemma"

    class Wordform(BaseModel):
        class Meta:
            table_name = "wordform"

    class Phrase(BaseModel):
        class Meta:
            table_name = "phrase"

    class Sentence(BaseModel):
        language_level = pw.CharField(null=True)

        class Meta:
            table_name = "sentence"

    class Sourcedir(BaseModel):

        class Meta:
            table_name = "sourcedir"

    class Sourcefile(BaseModel):
        publication_date = pw.DateTimeField(null=True)
        num_words = pw.IntegerField(null=True)
        language_level = pw.CharField(null=True)
        url = pw.CharField(null=True)
        title_target = pw.CharField(null=True)

        class Meta:
            table_name = "sourcefile"

    with database.atomic():
        # Add language_level to Lemma
        migrator.add_fields(
            Lemma,
            language_level=pw.CharField(null=True),
        )

        # Add language_level to Sentence
        migrator.add_fields(
            Sentence,
            language_level=pw.CharField(null=True),
        )

        # Add several new fields to Sourcefile
        migrator.add_fields(
            Sourcefile,
            publication_date=pw.DateTimeField(null=True),
            num_words=pw.IntegerField(null=True),
            language_level=pw.CharField(null=True),
            url=pw.CharField(null=True),
            title_target=pw.CharField(null=True),
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove the added fields from all models."""

    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Lemma(BaseModel):
        class Meta:
            table_name = "lemma"

    class Wordform(BaseModel):
        class Meta:
            table_name = "wordform"

    class Phrase(BaseModel):
        class Meta:
            table_name = "phrase"

    class Sentence(BaseModel):
        class Meta:
            table_name = "sentence"

    class Sourcedir(BaseModel):
        class Meta:
            table_name = "sourcedir"

    class Sourcefile(BaseModel):
        class Meta:
            table_name = "sourcefile"

    # Remove fields from Lemma
    with database.atomic():
        migrator.remove_fields(Lemma, "language_level")

    # Remove fields from Sentence
    with database.atomic():
        migrator.remove_fields(Sentence, "language_level")

    # Remove fields from Sourcefile
    with database.atomic():
        migrator.remove_fields(
            Sourcefile,
            "publication_date",
            "num_words",
            "language_level",
            "url",
            "title_target",
        )
