"""Peewee migrations -- 043_create_lemma_audio.py.

Create lemmaaudio table to store multiple audio variants (provider/voice) per lemma.
Follows cross-schema FK guidance in backend/docs/MIGRATIONS.md.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake: bool = False):
    # Unmanaged reference for auth.users
    class AuthUser(pw.Model):
        id = pw.UUIDField(primary_key=True)

        class Meta:
            table_name = "users"
            schema = "auth"

    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()

        class Meta:
            table_name = "basemodel"

    class Lemma(BaseModel):
        lemma = pw.CharField()
        target_language_code = pw.CharField()

        class Meta:
            table_name = "lemma"

    class LemmaAudio(BaseModel):
        lemma = pw.ForeignKeyField(Lemma, backref="audio_variants")
        provider = pw.CharField(default="elevenlabs")
        voice_name = pw.CharField()
        audio_data = pw.BlobField()
        created_by = pw.ForeignKeyField(AuthUser, null=True, backref="lemma_audio")

        class Meta:
            table_name = "lemmaaudio"

    with database.atomic():
        migrator.create_model(LemmaAudio)

        # Unique index on (lemma_id, provider, voice_name)
        migrator.sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS lemmaaudio_uniq ON lemmaaudio (lemma_id, provider, voice_name);"
        )
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS lemmaaudio_lemma_id_idx ON lemmaaudio (lemma_id);"
        )

        # Ensure CASCADE for lemma FK
        migrator.sql(
            "ALTER TABLE lemmaaudio DROP CONSTRAINT IF EXISTS lemmaaudio_lemma_id_fkey;"
        )
        migrator.sql(
            "ALTER TABLE lemmaaudio ADD CONSTRAINT lemmaaudio_lemma_id_fkey FOREIGN KEY (lemma_id) REFERENCES lemma(id) ON DELETE CASCADE;"
        )

        # Cross-schema FK for created_by → auth.users
        migrator.sql(
            "ALTER TABLE lemmaaudio DROP CONSTRAINT IF EXISTS fk_lemmaaudio_created_by_id;"
        )
        migrator.sql(
            """
            ALTER TABLE "lemmaaudio"
            ADD CONSTRAINT fk_lemmaaudio_created_by_id
            FOREIGN KEY ("created_by_id")
            REFERENCES "auth"."users" ("id")
            ON DELETE CASCADE;
            """
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake: bool = False):
    class LemmaAudio(pw.Model):
        class Meta:
            table_name = "lemmaaudio"

    with database.atomic():
        migrator.remove_model(LemmaAudio, cascade=True)





