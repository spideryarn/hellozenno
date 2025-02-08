"""Peewee migrations -- 012_add_cascade_delete_to_sourcefilephrase.py.

Add ON DELETE CASCADE behavior to the sourcefilephrase.sourcefile_id foreign key constraint
to match the model definition in db_models.py. This ensures that when a sourcefile is deleted,
its associated phrases are also deleted automatically.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add ON DELETE CASCADE to sourcefilephrase.sourcefile_id foreign key."""
    migrator.sql(
        """
        ALTER TABLE sourcefilephrase 
        DROP CONSTRAINT sourcefilephrase_sourcefile_id_fkey,
        ADD CONSTRAINT sourcefilephrase_sourcefile_id_fkey 
        FOREIGN KEY (sourcefile_id) 
        REFERENCES sourcefile(id) 
        ON DELETE CASCADE;
    """
    )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove ON DELETE CASCADE from sourcefilephrase.sourcefile_id foreign key."""
    migrator.sql(
        """
        ALTER TABLE sourcefilephrase 
        DROP CONSTRAINT sourcefilephrase_sourcefile_id_fkey,
        ADD CONSTRAINT sourcefilephrase_sourcefile_id_fkey 
        FOREIGN KEY (sourcefile_id) 
        REFERENCES sourcefile(id);
    """
    )
