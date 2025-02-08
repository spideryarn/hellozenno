"""Add sourcefile_type field to Sourcefile.

This migration adds a sourcefile_type field to track whether a Sourcefile was created from an image or text.
"""

from peewee import (
    Model,
    CharField,
    TextField,
    BlobField,
    DateTimeField,
    ForeignKeyField,
)
from playhouse.postgres_ext import JSONField


def migrate(migrator, database, **kwargs):
    """Add sourcefile_type field and populate it for existing records."""

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
        slug = CharField()

        class Meta:
            table_name = "sourcefile"

    # Step 1: Add column as nullable with no default
    migrator.sql("ALTER TABLE sourcefile ADD COLUMN sourcefile_type VARCHAR")

    # Step 2: Fill existing rows - all existing files are image type
    migrator.sql("UPDATE sourcefile SET sourcefile_type = 'image'")

    # Step 3: Make it required
    migrator.sql("ALTER TABLE sourcefile ALTER COLUMN sourcefile_type SET NOT NULL")


def rollback(migrator, database, **kwargs):
    """Remove sourcefile_type field."""
    migrator.remove_column("sourcefile", "sourcefile_type")
