"""Add slug field to Sourcedir."""

from peewee import Model, CharField, DateTimeField
from slugify import slugify

from api.config import SOURCEDIR_SLUG_MAX_LENGTH


def migrate(migrator, database, **kwargs):
    """Add slug field and populate it for existing records."""

    # Define model class for column operations
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcedir(BaseModel):
        path = CharField(unique=True)
        language_code = CharField(max_length=2)
        slug = CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH)

        class Meta:
            table_name = "sourcedir"

    # Step 1: Add column as nullable with default
    migrator.add_columns(
        Sourcedir,
        slug=CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH, null=True),
    )

    # Step 2: Fill existing rows
    with database.atomic():
        # First get all paths
        cursor = database.execute_sql("SELECT id, path FROM sourcedir")
        rows = cursor.fetchall()

        # Then update each row with its slug
        for row_id, path in rows:
            slug = slugify(str(path))
            database.execute_sql(
                "UPDATE sourcedir SET slug = %s WHERE id = %s", (slug, row_id)
            )

    # Step 3: Make it required and add unique index
    with database.atomic():
        migrator.sql("ALTER TABLE sourcedir ALTER COLUMN slug SET NOT NULL")
        migrator.sql(
            'CREATE UNIQUE INDEX "sourcedir_slug_language_code" ON sourcedir (slug, language_code)'
        )


def rollback(migrator, database, **kwargs):
    """Remove slug field."""

    # Define model class for column operations
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcedir(BaseModel):
        path = CharField(unique=True)
        language_code = CharField(max_length=2)
        slug = CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH)

        class Meta:
            table_name = "sourcedir"

    migrator.sql('DROP INDEX IF EXISTS "sourcedir_slug_language_code"')
    migrator.remove_fields(Sourcedir, "slug", cascade=True)
