"""Peewee migrations -- 041_add_profile_admin_granted_at.py.

Add admin_granted_at column to public.profile to store admin role grant time.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext  # noqa: F401


def migrate(migrator: Migrator, database: pw.Database, **kwargs):
    class Profile(pw.Model):
        class Meta:
            table_name = "profile"

    with database.atomic():
        migrator.add_fields(
            Profile,
            admin_granted_at=pw.DateTimeField(null=True),
        )


def rollback(migrator: Migrator, database: pw.Database, **kwargs):
    class Profile(pw.Model):
        class Meta:
            table_name = "profile"

    with database.atomic():
        migrator.drop_columns(Profile, ["admin_granted_at"])
