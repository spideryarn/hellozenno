"""Peewee migrations -- 026_add_cascade_delete_to_remaining_constraints.py.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    # Use database.atomic() to ensure the migration is wrapped in a transaction
    with database.atomic():
        # We're excluding Supabase storage-related tables (objects, s3_multipart_uploads, s3_multipart_uploads_parts)

        # 1. lemmaexamplesentence_sentence_id_fkey
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" DROP CONSTRAINT "lemmaexamplesentence_sentence_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" ADD CONSTRAINT "lemmaexamplesentence_sentence_id_fkey" '
            'FOREIGN KEY ("sentence_id") REFERENCES "sentence" ("id") ON DELETE CASCADE;'
        )

        # 2. phraseexamplesentence_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" DROP CONSTRAINT "phraseexamplesentence_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" ADD CONSTRAINT "phraseexamplesentence_phrase_id_fkey" '
            'FOREIGN KEY ("phrase_id") REFERENCES "phrase" ("id") ON DELETE CASCADE;'
        )

        # 3. phraseexamplesentence_sentence_id_fkey
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" DROP CONSTRAINT "phraseexamplesentence_sentence_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" ADD CONSTRAINT "phraseexamplesentence_sentence_id_fkey" '
            'FOREIGN KEY ("sentence_id") REFERENCES "sentence" ("id") ON DELETE CASCADE;'
        )

        # 4. relatedphrase_from_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "relatedphrase" DROP CONSTRAINT "relatedphrase_from_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "relatedphrase" ADD CONSTRAINT "relatedphrase_from_phrase_id_fkey" '
            'FOREIGN KEY ("from_phrase_id") REFERENCES "phrase" ("id") ON DELETE CASCADE;'
        )

        # 5. relatedphrase_to_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "relatedphrase" DROP CONSTRAINT "relatedphrase_to_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "relatedphrase" ADD CONSTRAINT "relatedphrase_to_phrase_id_fkey" '
            'FOREIGN KEY ("to_phrase_id") REFERENCES "phrase" ("id") ON DELETE CASCADE;'
        )

        # 6. sourcefile_sourcedir_id_fkey
        migrator.sql(
            'ALTER TABLE "sourcefile" DROP CONSTRAINT "sourcefile_sourcedir_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "sourcefile" ADD CONSTRAINT "sourcefile_sourcedir_id_fkey" '
            'FOREIGN KEY ("sourcedir_id") REFERENCES "sourcedir" ("id") ON DELETE CASCADE;'
        )

        # 7. sourcefilephrase_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "sourcefilephrase" DROP CONSTRAINT "sourcefilephrase_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "sourcefilephrase" ADD CONSTRAINT "sourcefilephrase_phrase_id_fkey" '
            'FOREIGN KEY ("phrase_id") REFERENCES "phrase" ("id") ON DELETE CASCADE;'
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    # Use database.atomic() to ensure the rollback is wrapped in a transaction
    with database.atomic():
        # 1. lemmaexamplesentence_sentence_id_fkey
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" DROP CONSTRAINT "lemmaexamplesentence_sentence_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" ADD CONSTRAINT "lemmaexamplesentence_sentence_id_fkey" '
            'FOREIGN KEY ("sentence_id") REFERENCES "sentence" ("id");'
        )

        # 2. phraseexamplesentence_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" DROP CONSTRAINT "phraseexamplesentence_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" ADD CONSTRAINT "phraseexamplesentence_phrase_id_fkey" '
            'FOREIGN KEY ("phrase_id") REFERENCES "phrase" ("id");'
        )

        # 3. phraseexamplesentence_sentence_id_fkey
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" DROP CONSTRAINT "phraseexamplesentence_sentence_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "phraseexamplesentence" ADD CONSTRAINT "phraseexamplesentence_sentence_id_fkey" '
            'FOREIGN KEY ("sentence_id") REFERENCES "sentence" ("id");'
        )

        # 4. relatedphrase_from_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "relatedphrase" DROP CONSTRAINT "relatedphrase_from_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "relatedphrase" ADD CONSTRAINT "relatedphrase_from_phrase_id_fkey" '
            'FOREIGN KEY ("from_phrase_id") REFERENCES "phrase" ("id");'
        )

        # 5. relatedphrase_to_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "relatedphrase" DROP CONSTRAINT "relatedphrase_to_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "relatedphrase" ADD CONSTRAINT "relatedphrase_to_phrase_id_fkey" '
            'FOREIGN KEY ("to_phrase_id") REFERENCES "phrase" ("id");'
        )

        # 6. sourcefile_sourcedir_id_fkey
        migrator.sql(
            'ALTER TABLE "sourcefile" DROP CONSTRAINT "sourcefile_sourcedir_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "sourcefile" ADD CONSTRAINT "sourcefile_sourcedir_id_fkey" '
            'FOREIGN KEY ("sourcedir_id") REFERENCES "sourcedir" ("id");'
        )

        # 7. sourcefilephrase_phrase_id_fkey
        migrator.sql(
            'ALTER TABLE "sourcefilephrase" DROP CONSTRAINT "sourcefilephrase_phrase_id_fkey";'
        )
        migrator.sql(
            'ALTER TABLE "sourcefilephrase" ADD CONSTRAINT "sourcefilephrase_phrase_id_fkey" '
            'FOREIGN KEY ("phrase_id") REFERENCES "phrase" ("id");'
        )
