"""Peewee migrations -- 036_fix_sourcedir_path_constraint.py.

This migration removes the unexpected unique constraint on just the 'path' column
in the sourcedir table, which is causing issues with the get_or_create_ai_sourcedir
function in generate_sourcefiles.py.

The constraint is not part of the model definition in db_models.py, but exists
in the database, preventing the creation of sourcedirs with the same path for
different languages.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove the unique constraint on the 'path' column in the sourcedir table."""

    with database.atomic():
        # Drop the unique constraint on just the path column
        migrator.sql('DROP INDEX IF EXISTS "sourcedir_path";')


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Recreate the unique constraint on the 'path' column if needed."""
    
    with database.atomic():
        # Recreate the unique index if desired
        migrator.sql('CREATE UNIQUE INDEX sourcedir_path ON public.sourcedir USING btree (path);')
