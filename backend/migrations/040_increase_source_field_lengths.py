from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    class Sourcedir(pw.Model):
        path = pw.CharField(max_length=255)  # Original max_length
        slug = pw.CharField(max_length=100)  # Original max_length

        class Meta:
            table_name = "sourcedir"

    class Sourcefile(pw.Model):
        filename = pw.CharField(max_length=100)  # Original max_length
        slug = pw.CharField(max_length=100)  # Original max_length
        audio_filename = pw.CharField(max_length=255, null=True)  # Original max_length
        url = pw.CharField(max_length=255, null=True)  # Original max_length
        title_target = pw.CharField(max_length=255, null=True)  # Original max_length

        class Meta:
            table_name = "sourcefile"

    with database.atomic():
        migrator.change_fields(
            Sourcedir,
            path=pw.CharField(max_length=1024),
            slug=pw.CharField(max_length=1024),
        )
        migrator.change_fields(
            Sourcefile,
            filename=pw.CharField(max_length=1024),
            slug=pw.CharField(max_length=1024),
            audio_filename=pw.CharField(max_length=1024, null=True),
            url=pw.CharField(max_length=2048, null=True),
            title_target=pw.CharField(max_length=2048, null=True),
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    class Sourcedir(pw.Model):
        # Fields here don't need original max_length for rollback to change_fields
        class Meta:
            table_name = "sourcedir"

    class Sourcefile(pw.Model):
        class Meta:
            table_name = "sourcefile"

    with database.atomic():
        migrator.change_fields(
            Sourcedir,
            path=pw.CharField(max_length=255),
            slug=pw.CharField(max_length=100),
        )
        migrator.change_fields(
            Sourcefile,
            filename=pw.CharField(max_length=100),
            slug=pw.CharField(max_length=100),
            audio_filename=pw.CharField(max_length=255, null=True),
            url=pw.CharField(max_length=255, null=True),
            title_target=pw.CharField(max_length=255, null=True),
        )
