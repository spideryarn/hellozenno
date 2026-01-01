"""Add sourcefile_id and sourcedir_id FKs to Sentence for source tracking.

This fixes Bug #2: sentence metadata overwrites when same text is generated
for different sources. With separate FKs, each source can have its own
sentence record without corrupting others.

Usage:
- Sourcefile-level learn: sourcefile_id = X, sourcedir_id = NULL
- Sourcedir-level learn: sourcefile_id = NULL, sourcedir_id = Y
- Manual/imported: sourcefile_id = NULL, sourcedir_id = NULL

CHECK constraint ensures only one FK can be set at a time.
Partial unique indexes handle each case.
"""

import peewee as pw


def migrate(migrator, database, **kwargs):
    class Sourcedir(pw.Model):
        class Meta:
            table_name = "sourcedir"

    class Sourcefile(pw.Model):
        class Meta:
            table_name = "sourcefile"

    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    with database.atomic():
        # 1. Add sourcefile_id FK (nullable)
        migrator.add_fields(
            Sentence,
            sourcefile_id=pw.IntegerField(null=True),
        )

        # 2. Add sourcedir_id FK (nullable)
        migrator.add_fields(
            Sentence,
            sourcedir_id=pw.IntegerField(null=True),
        )

        # 3. Add FK constraints
        migrator.sql(
            """
            ALTER TABLE sentence
            ADD CONSTRAINT fk_sentence_sourcefile
            FOREIGN KEY (sourcefile_id) REFERENCES sourcefile(id)
            ON DELETE SET NULL;
            """
        )
        migrator.sql(
            """
            ALTER TABLE sentence
            ADD CONSTRAINT fk_sentence_sourcedir
            FOREIGN KEY (sourcedir_id) REFERENCES sourcedir(id)
            ON DELETE SET NULL;
            """
        )

        # 4. Add CHECK constraint: at most one FK can be set
        migrator.sql(
            """
            ALTER TABLE sentence
            ADD CONSTRAINT chk_sentence_source_exclusive
            CHECK (NOT (sourcefile_id IS NOT NULL AND sourcedir_id IS NOT NULL));
            """
        )

        # 5. Drop the old unique constraint on (sentence, target_language_code)
        migrator.sql(
            'DROP INDEX IF EXISTS "sentence_sentence_target_language_code";'
        )

        # 6. Drop the old slug unique constraint
        migrator.sql(
            'DROP INDEX IF EXISTS "sentence_slug_target_language_code";'
        )

        # 7. Create partial unique index for manual sentences (both FKs NULL)
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_text_lang_manual
            ON sentence (sentence, target_language_code)
            WHERE sourcefile_id IS NULL AND sourcedir_id IS NULL;
            """
        )

        # 8. Create partial unique index for sourcefile-level sentences
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_text_lang_sourcefile
            ON sentence (sentence, target_language_code, sourcefile_id)
            WHERE sourcefile_id IS NOT NULL;
            """
        )

        # 9. Create partial unique index for sourcedir-level sentences
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_text_lang_sourcedir
            ON sentence (sentence, target_language_code, sourcedir_id)
            WHERE sourcedir_id IS NOT NULL;
            """
        )

        # 10. Create partial unique index for slug with manual sentences
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_slug_lang_manual
            ON sentence (slug, target_language_code)
            WHERE sourcefile_id IS NULL AND sourcedir_id IS NULL;
            """
        )

        # 11. Create partial unique index for slug with sourcefile
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_slug_lang_sourcefile
            ON sentence (slug, target_language_code, sourcefile_id)
            WHERE sourcefile_id IS NOT NULL;
            """
        )

        # 12. Create partial unique index for slug with sourcedir
        migrator.sql(
            """
            CREATE UNIQUE INDEX sentence_slug_lang_sourcedir
            ON sentence (slug, target_language_code, sourcedir_id)
            WHERE sourcedir_id IS NOT NULL;
            """
        )

        # 13. Add indexes on FKs for efficient lookups
        migrator.sql(
            """
            CREATE INDEX sentence_sourcefile_id_idx
            ON sentence (sourcefile_id)
            WHERE sourcefile_id IS NOT NULL;
            """
        )
        migrator.sql(
            """
            CREATE INDEX sentence_sourcedir_id_idx
            ON sentence (sourcedir_id)
            WHERE sourcedir_id IS NOT NULL;
            """
        )


def rollback(migrator, database, **kwargs):
    class Sentence(pw.Model):
        class Meta:
            table_name = "sentence"

    with database.atomic():
        # Drop FK constraints
        migrator.sql(
            'ALTER TABLE sentence DROP CONSTRAINT IF EXISTS fk_sentence_sourcefile;'
        )
        migrator.sql(
            'ALTER TABLE sentence DROP CONSTRAINT IF EXISTS fk_sentence_sourcedir;'
        )
        migrator.sql(
            'ALTER TABLE sentence DROP CONSTRAINT IF EXISTS chk_sentence_source_exclusive;'
        )

        # Drop the new indexes
        migrator.sql('DROP INDEX IF EXISTS "sentence_text_lang_manual";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_text_lang_sourcefile";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_text_lang_sourcedir";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_slug_lang_manual";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_slug_lang_sourcefile";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_slug_lang_sourcedir";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_sourcefile_id_idx";')
        migrator.sql('DROP INDEX IF EXISTS "sentence_sourcedir_id_idx";')

        # Recreate the original unique indexes
        migrator.sql(
            """
            CREATE UNIQUE INDEX "sentence_sentence_target_language_code"
            ON sentence (sentence, target_language_code);
            """
        )
        migrator.sql(
            """
            CREATE UNIQUE INDEX "sentence_slug_target_language_code"
            ON sentence (slug, target_language_code);
            """
        )

        # Drop the FK columns
        migrator.drop_columns(Sentence, ["sourcefile_id", "sourcedir_id"])
