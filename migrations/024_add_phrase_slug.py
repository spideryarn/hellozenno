"""Add slug field to Phrase model for URL-friendly identifiers.

This migration adds a slug field to the Phrase model, which will be used in URLs
instead of the canonical_form to avoid issues with special characters.
"""

from contextlib import suppress
import peewee as pw
from peewee_migrate import Migrator
from slugify import slugify

with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add slug field to Phrase model and populate it for existing records."""
    if fake:
        return

    # Define model classes for column operations
    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()

    class Phrase(BaseModel):
        canonical_form = pw.CharField()
        language_code = pw.CharField()
        slug = pw.CharField(max_length=255, null=True)

        class Meta:
            table_name = "phrase"

    with database.atomic():
        # Step 1: Add the slug column as nullable
        migrator.add_columns(Phrase, slug=pw.CharField(max_length=255, null=True))

        # Step 2: Fill existing rows with slugs generated from canonical_form
        # Get all phrases
        phrases = database.execute_sql(
            "SELECT id, canonical_form FROM phrase"
        ).fetchall()

        # Update each phrase with a generated slug
        for phrase_id, canonical_form in phrases:
            slug = slugify(str(canonical_form))
            # Truncate slug if it exceeds max length
            if len(slug) > 255:
                slug = slug[:255]

            # Update the phrase with the generated slug
            migrator.sql("UPDATE phrase SET slug = %s WHERE id = %s", (slug, phrase_id))

        # Step 3: Add a unique index on (slug, language_code)
        migrator.sql(
            'CREATE UNIQUE INDEX "phrase_slug_language_code" ON phrase (slug, language_code);'
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove slug field and related index from Phrase model."""
    if fake:
        return

    # Define model classes for column operations
    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()

    class Phrase(BaseModel):
        canonical_form = pw.CharField()
        language_code = pw.CharField()
        slug = pw.CharField(max_length=255, null=True)

        class Meta:
            table_name = "phrase"

    with database.atomic():
        # Step 1: Drop the unique index
        migrator.sql('DROP INDEX IF EXISTS "phrase_slug_language_code";')

        # Step 2: Drop the slug column
        migrator.remove_fields(Phrase, "slug")
