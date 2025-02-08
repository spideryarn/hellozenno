"""Make SourcefileWordform.centrality nullable.

When wordforms are auto-discovered during interactive word previews, we don't have
centrality information from the LLM, so the field should be nullable.
"""

from peewee_migrate import Migrator


def migrate(migrator: Migrator, database, **kwargs):
    """Make centrality field nullable."""
    with database.atomic():
        migrator.sql(
            'ALTER TABLE "sourcefilewordform" ALTER COLUMN "centrality" DROP NOT NULL;'
        )


def rollback(migrator: Migrator, database, **kwargs):
    """Make centrality field required again."""
    with database.atomic():
        migrator.sql(
            'ALTER TABLE "sourcefilewordform" ALTER COLUMN "centrality" SET NOT NULL;'
        )
