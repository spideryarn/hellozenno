"""Add slug field to Sentence model and populate with slugs."""

from peewee import CharField, Model, TextField
from peewee_migrate import Migrator
from playhouse.postgres_ext import JSONField
from slugify import slugify


class Sentence(Model):
    sentence = TextField()
    language_code = CharField()

    class Meta:
        table_name = "sentence"


def migrate(migrator: Migrator, database, *, fake=False):
    """Add slug field and populate with slugs."""

    # Step 1: Add nullable slug field
    migrator.sql("ALTER TABLE sentence ADD COLUMN slug VARCHAR(255)")

    # Step 2: Fill existing rows with slugs using Python slugify
    with database.bind_ctx([Sentence]):
        with database.atomic():
            # Process in batches to avoid memory issues
            batch_size = 1000
            for sentence in Sentence.select().iterator():
                slug = slugify(str(sentence.sentence))
                if len(slug) > 255:
                    slug = slug[:255]
                migrator.sql(
                    "UPDATE sentence SET slug = %s WHERE id = %s", (slug, sentence.id)
                )


def rollback(migrator: Migrator, database, *, fake=False):
    """Remove slug field."""
    migrator.sql("ALTER TABLE sentence DROP COLUMN slug")
