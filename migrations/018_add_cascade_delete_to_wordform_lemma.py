"""Peewee migrations -- 018_add_cascade_delete_to_wordform_lemma.py.

Add ON DELETE CASCADE behavior to the wordform.lemma_entry_id foreign key constraint
to match the model definition in db_models.py. This ensures that when a lemma is deleted,
its associated wordforms are also deleted automatically.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add ON DELETE CASCADE to wordform.lemma_entry_id foreign key."""
    migrator.sql(
        """
        ALTER TABLE wordform 
        DROP CONSTRAINT wordform_lemma_entry_id_fkey,
        ADD CONSTRAINT wordform_lemma_entry_id_fkey 
        FOREIGN KEY (lemma_entry_id) 
        REFERENCES lemma(id) 
        ON DELETE CASCADE;
        """
    )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove ON DELETE CASCADE from wordform.lemma_entry_id foreign key."""
    migrator.sql(
        """
        ALTER TABLE wordform 
        DROP CONSTRAINT wordform_lemma_entry_id_fkey,
        ADD CONSTRAINT wordform_lemma_entry_id_fkey 
        FOREIGN KEY (lemma_entry_id) 
        REFERENCES lemma(id);
        """
    )
