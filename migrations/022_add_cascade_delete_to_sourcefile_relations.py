"""Peewee migrations -- 022_add_cascade_delete_to_sourcefile_relations.py.

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
    """Write your migrations here."""

    # Use database.atomic() to ensure the migration is wrapped in a transaction
    with database.atomic():
        # First, drop the existing foreign key constraints
        migrator.sql(
            "ALTER TABLE sourcefilewordform DROP CONSTRAINT IF EXISTS sourcefilewordform_sourcefile_id_fkey"
        )
        migrator.sql(
            "ALTER TABLE sourcefilephrase DROP CONSTRAINT IF EXISTS sourcefilephrase_sourcefile_id_fkey"
        )

        # Then add the constraints back with ON DELETE CASCADE
        migrator.sql(
            "ALTER TABLE sourcefilewordform ADD CONSTRAINT sourcefilewordform_sourcefile_id_fkey "
            "FOREIGN KEY (sourcefile_id) REFERENCES sourcefile(id) ON DELETE CASCADE"
        )
        migrator.sql(
            "ALTER TABLE sourcefilephrase ADD CONSTRAINT sourcefilephrase_sourcefile_id_fkey "
            "FOREIGN KEY (sourcefile_id) REFERENCES sourcefile(id) ON DELETE CASCADE"
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    # Use database.atomic() to ensure the rollback is wrapped in a transaction
    with database.atomic():
        # First, drop the CASCADE constraints
        migrator.sql(
            "ALTER TABLE sourcefilewordform DROP CONSTRAINT IF EXISTS sourcefilewordform_sourcefile_id_fkey"
        )
        migrator.sql(
            "ALTER TABLE sourcefilephrase DROP CONSTRAINT IF EXISTS sourcefilephrase_sourcefile_id_fkey"
        )

        # Then add the constraints back without CASCADE
        migrator.sql(
            "ALTER TABLE sourcefilewordform ADD CONSTRAINT sourcefilewordform_sourcefile_id_fkey "
            "FOREIGN KEY (sourcefile_id) REFERENCES sourcefile(id)"
        )
        migrator.sql(
            "ALTER TABLE sourcefilephrase ADD CONSTRAINT sourcefilephrase_sourcefile_id_fkey "
            "FOREIGN KEY (sourcefile_id) REFERENCES sourcefile(id)"
        )
