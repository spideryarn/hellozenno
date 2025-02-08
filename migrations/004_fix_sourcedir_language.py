"""Fix sourcedir table by adding language_code and updating unique index."""

from peewee import CharField, Model, DateTimeField


def migrate(migrator, database, *, fake=False):
    """Add language_code to sourcedir and update unique index."""
    if fake:
        return

    # Define model class for column operations
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcedir(BaseModel):
        path = CharField(unique=True)
        language_code = CharField(max_length=2)

        class Meta:
            table_name = "sourcedir"

    with database.atomic():
        # Drop the old unique index on path
        migrator.sql('DROP INDEX IF EXISTS "idx_17635_sourcedir_path";')

        # Add language_code column with default value initially
        migrator.add_columns(
            Sourcedir,
            language_code=CharField(max_length=2, default="el"),
        )

        # Now alter the column to remove default and make it required
        migrator.sql("ALTER TABLE sourcedir ALTER COLUMN language_code SET NOT NULL;")
        migrator.sql("ALTER TABLE sourcedir ALTER COLUMN language_code DROP DEFAULT;")

        # Add new composite unique index
        migrator.sql(
            'CREATE UNIQUE INDEX "sourcedir_path_language_code" ON sourcedir (path, language_code);'
        )


def rollback(migrator, database, *, fake=False):
    """Rollback the migration."""
    if fake:
        return

    # Define model class for column operations
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Sourcedir(BaseModel):
        path = CharField(unique=True)
        language_code = CharField(max_length=2)

        class Meta:
            table_name = "sourcedir"

    with database.atomic():
        # Drop the composite unique index
        migrator.sql('DROP INDEX IF EXISTS "sourcedir_path_language_code";')

        # Drop the language_code column
        migrator.drop_column(Sourcedir, "language_code")

        # Re-add the original unique index on path
        migrator.sql(
            'CREATE UNIQUE INDEX "idx_17635_sourcedir_path" ON sourcedir (path);'
        )
