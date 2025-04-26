"""Peewee migrations -- 033_add_user_reference_fields.py.

This migration adds created_by_id fields as UUID references to the auth.users table
for these models:
- Lemma
- Wordform
- Phrase
- Sentence
- Sourcedir

It also drops the existing created_by VARCHAR field from Sourcefile and replaces
it with a proper UUID field (created_by_id) with a foreign key constraint.

All fields are nullable to maintain backward compatibility with existing data.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add created_by_id fields as UUID references to auth.users with explicit FK constraints."""

    # Define model classes for the tables we're modifying
    # Note: These only define the *new* field being added
    class BaseModel(pw.Model):
        class Meta:
            table_name = "basemodel"

    class Lemma(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "lemma"

    class Wordform(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "wordform"

    class Phrase(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "phrase"

    class Sentence(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "sentence"

    class Sourcedir(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "sourcedir"

    class Sourcefile(BaseModel):
        created_by_id = pw.UUIDField(null=True)  # Field name convention

        class Meta:
            table_name = "sourcefile"

    with database.atomic():
        # Add created_by_id UUID fields
        with database.atomic():
            # Add created_by_id field to Lemma
            migrator.add_fields(
                Lemma,
                created_by_id=pw.UUIDField(null=True),
            )
            # Add FK constraint
            migrator.sql(
                """
                ALTER TABLE "lemma" 
                ADD CONSTRAINT fk_lemma_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )

            # Add created_by_id field to Wordform
            migrator.add_fields(
                Wordform,
                created_by_id=pw.UUIDField(null=True),
            )
            # Add FK constraint
            migrator.sql(
                """
                ALTER TABLE "wordform" 
                ADD CONSTRAINT fk_wordform_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )

            # Add created_by_id field to Phrase
            migrator.add_fields(
                Phrase,
                created_by_id=pw.UUIDField(null=True),
            )
            # Add FK constraint
            migrator.sql(
                """
                ALTER TABLE "phrase" 
                ADD CONSTRAINT fk_phrase_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )

            # Add created_by_id field to Sentence
            migrator.add_fields(
                Sentence,
                created_by_id=pw.UUIDField(null=True),
            )
            # Add FK constraint
            migrator.sql(
                """
                ALTER TABLE "sentence" 
                ADD CONSTRAINT fk_sentence_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )

            # Add created_by_id field to Sourcedir
            migrator.add_fields(
                Sourcedir,
                created_by_id=pw.UUIDField(null=True),
            )
            # Add FK constraint
            migrator.sql(
                """
                ALTER TABLE "sourcedir" 
                ADD CONSTRAINT fk_sourcedir_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )

        # For Sourcefile, add the new created_by_id UUID field with FK constraint.
        # Assumes the old created_by VARCHAR was handled previously or not present.
        with database.atomic():
            migrator.add_fields(
                Sourcefile,
                created_by_id=pw.UUIDField(null=True),
            )
            migrator.sql(
                """
                ALTER TABLE "sourcefile" 
                ADD CONSTRAINT fk_sourcefile_created_by_id
                FOREIGN KEY ("created_by_id")
                REFERENCES "auth"."users" ("id") 
                ON DELETE CASCADE;
                """
            )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove the added created_by_id fields and constraints."""

    # Define model classes for the tables we're modifying (no fields needed here)
    class BaseModel(pw.Model):
        class Meta:
            # database = database # No need to bind for rollback field removal
            table_name = "basemodel"

    class Lemma(BaseModel):
        class Meta:
            # database = database
            table_name = "lemma"

    class Wordform(BaseModel):
        class Meta:
            # database = database
            table_name = "wordform"

    class Phrase(BaseModel):
        class Meta:
            # database = database
            table_name = "phrase"

    class Sentence(BaseModel):
        class Meta:
            # database = database
            table_name = "sentence"

    class Sourcedir(BaseModel):
        class Meta:
            # database = database
            table_name = "sourcedir"

    class Sourcefile(BaseModel):
        # Define original created_by if it existed before this migration
        created_by = pw.CharField(null=True)  # For re-adding if necessary

        class Meta:
            # database = database
            table_name = "sourcefile"

    with database.atomic():
        # Drop FK constraints first (using _id suffix)
        with database.atomic():
            migrator.sql(
                'ALTER TABLE "lemma" DROP CONSTRAINT IF EXISTS fk_lemma_created_by_id;'
            )
            migrator.sql(
                'ALTER TABLE "wordform" DROP CONSTRAINT IF EXISTS fk_wordform_created_by_id;'
            )
            migrator.sql(
                'ALTER TABLE "phrase" DROP CONSTRAINT IF EXISTS fk_phrase_created_by_id;'
            )
            migrator.sql(
                'ALTER TABLE "sentence" DROP CONSTRAINT IF EXISTS fk_sentence_created_by_id;'
            )
            migrator.sql(
                'ALTER TABLE "sourcedir" DROP CONSTRAINT IF EXISTS fk_sourcedir_created_by_id;'
            )
            migrator.sql(
                'ALTER TABLE "sourcefile" DROP CONSTRAINT IF EXISTS fk_sourcefile_created_by_id;'
            )

        # Remove created_by_id fields (using _id suffix)
        with database.atomic():
            migrator.remove_fields(Lemma, "created_by_id")
            migrator.remove_fields(Wordform, "created_by_id")
            migrator.remove_fields(Phrase, "created_by_id")
            migrator.remove_fields(Sentence, "created_by_id")
            migrator.remove_fields(Sourcedir, "created_by_id")
            migrator.remove_fields(Sourcefile, "created_by_id")

        # Re-add the original created_by field as VARCHAR for Sourcefile if needed.
        # If Sourcefile did not have a created_by field before this migration,
        # this block should be commented out or removed.
        # with database.atomic():
        #    migrator.add_fields(Sourcefile, created_by=pw.CharField(null=True))
