"""Peewee migrations -- 030_rename_language_code_to_target_language_code.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Rename language_code field to target_language_code in all relevant models."""
    
    with database.atomic():
        # Explicitly rename each column with direct SQL commands
        migrator.sql("ALTER TABLE lemma RENAME COLUMN language_code TO target_language_code;")
        migrator.sql("ALTER TABLE wordform RENAME COLUMN language_code TO target_language_code;")
        migrator.sql("ALTER TABLE sentence RENAME COLUMN language_code TO target_language_code;")
        migrator.sql("ALTER TABLE phrase RENAME COLUMN language_code TO target_language_code;")
        migrator.sql("ALTER TABLE sourcedir RENAME COLUMN language_code TO target_language_code;")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Restore original field name."""
    
    with database.atomic():
        # Explicitly rename each column back with direct SQL commands
        migrator.sql("ALTER TABLE lemma RENAME COLUMN target_language_code TO language_code;")
        migrator.sql("ALTER TABLE wordform RENAME COLUMN target_language_code TO language_code;")
        migrator.sql("ALTER TABLE sentence RENAME COLUMN target_language_code TO language_code;")
        migrator.sql("ALTER TABLE phrase RENAME COLUMN target_language_code TO language_code;")
        migrator.sql("ALTER TABLE sourcedir RENAME COLUMN target_language_code TO language_code;")
