"""Peewee migrations -- 025_add_cascade_delete_to_lemmaexamplesentence.py.
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
        # First, drop the existing foreign key constraint
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" DROP CONSTRAINT "lemmaexamplesentence_lemma_id_fkey";'
        )

        # Then recreate it with ON DELETE CASCADE
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" ADD CONSTRAINT "lemmaexamplesentence_lemma_id_fkey" '
            'FOREIGN KEY ("lemma_id") REFERENCES "lemma" ("id") ON DELETE CASCADE;'
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    # Use database.atomic() to ensure the rollback is wrapped in a transaction
    with database.atomic():
        # First, drop the CASCADE constraint
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" DROP CONSTRAINT "lemmaexamplesentence_lemma_id_fkey";'
        )

        # Then recreate the original constraint without CASCADE
        migrator.sql(
            'ALTER TABLE "lemmaexamplesentence" ADD CONSTRAINT "lemmaexamplesentence_lemma_id_fkey" '
            'FOREIGN KEY ("lemma_id") REFERENCES "lemma" ("id");'
        )
