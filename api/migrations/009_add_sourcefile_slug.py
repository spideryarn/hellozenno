"""Add slug field to Sourcefile."""

from peewee import (
    Model,
    CharField,
    TextField,
    BlobField,
    DateTimeField,
    ForeignKeyField,
)
from playhouse.postgres_ext import JSONField
from slugify import slugify

from api.config import SOURCEFILE_SLUG_MAX_LENGTH


def migrate(migrator, database, **kwargs):
    """Add slug field and populate it for existing records."""

    # Define model class for column operations
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcedir(BaseModel):
        path = CharField()
        language_code = CharField(max_length=2)

        class Meta:
            table_name = "sourcedir"

    class Sourcefile(BaseModel):
        sourcedir = ForeignKeyField(Sourcedir, backref="sourcefiles")
        filename = CharField()
        image_data = BlobField(null=True)
        audio_data = BlobField(null=True)
        text_target = TextField()
        text_english = TextField()
        audio_filename = CharField(null=True)
        metadata = JSONField()
        slug = CharField(max_length=SOURCEFILE_SLUG_MAX_LENGTH)

        class Meta:
            table_name = "sourcefile"

    # Step 1: Add column as nullable with no default
    migrator.sql("ALTER TABLE sourcefile ADD COLUMN slug VARCHAR")

    # Step 2: Fill existing rows
    with database.atomic():
        # First get all filenames
        cursor = database.execute_sql("SELECT id, filename FROM sourcefile")
        rows = cursor.fetchall()

        # Then update each row with its slug
        for row_id, filename in rows:
            slug = slugify(str(filename))
            database.execute_sql(
                "UPDATE sourcefile SET slug = %s WHERE id = %s", (slug, row_id)
            )

    # Step 3: Make it required and add unique index
    with database.atomic():
        # Make it not null
        migrator.sql("ALTER TABLE sourcefile ALTER COLUMN slug SET NOT NULL")
        # Add unique index using raw SQL since Peewee's add_index is having issues
        migrator.sql(
            'CREATE UNIQUE INDEX "sourcefile_slug_sourcedir_id" ON sourcefile (slug, sourcedir_id)'
        )


def rollback(migrator, database, **kwargs):
    """Remove slug field."""
    with database.atomic():
        # Drop the unique index first
        migrator.sql('DROP INDEX IF EXISTS "sourcefile_slug_sourcedir_id"')
        # Then drop the column
        migrator.sql("ALTER TABLE sourcefile DROP COLUMN slug")
