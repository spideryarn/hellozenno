"""Add metadata JSON to lemmaaudio and drop voice_name column."""

import peewee as pw
from peewee_migrate import Migrator
from playhouse.postgres_ext import JSONField


def migrate(migrator: Migrator, database: pw.Database, **kwargs):
    class LemmaAudio(pw.Model):
        provider = pw.CharField(default="elevenlabs")
        voice_name = pw.CharField()
        metadata = JSONField(null=True)

        class Meta:
            table_name = "lemmaaudio"

    with database.atomic():
        migrator.add_fields(LemmaAudio, metadata=JSONField(null=True))

    with database.atomic():
        cursor = database.execute_sql("SELECT id, provider, voice_name FROM lemmaaudio")
        rows = cursor.fetchall()
        for row_id, provider, voice_name in rows:
            database.execute_sql(
                """
                UPDATE lemmaaudio
                SET metadata = jsonb_build_object('provider', %s, 'voice_name', %s)
                WHERE id = %s
                """,
                (provider, voice_name, row_id),
            )

        migrator.sql("ALTER TABLE lemmaaudio ALTER COLUMN metadata SET NOT NULL")
        migrator.sql("DROP INDEX IF EXISTS lemmaaudio_uniq")
        migrator.drop_columns(LemmaAudio, ["voice_name"])
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS lemmaaudio_lemma_id_created_at_idx ON lemmaaudio (lemma_id, created_at)"
        )


def rollback(migrator: Migrator, database: pw.Database, **kwargs):
    with database.atomic():
        migrator.sql("ALTER TABLE lemmaaudio ADD COLUMN voice_name VARCHAR")
        database.execute_sql(
            """
            UPDATE lemmaaudio
            SET voice_name = COALESCE(metadata->>'voice_name', provider)
            """
        )
        migrator.sql("ALTER TABLE lemmaaudio ALTER COLUMN voice_name SET NOT NULL")
        migrator.sql("DROP INDEX IF EXISTS lemmaaudio_lemma_id_created_at_idx")
        migrator.sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS lemmaaudio_uniq ON lemmaaudio (lemma_id, provider, voice_name)"
        )
