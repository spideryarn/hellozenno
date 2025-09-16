"""Create sentenceaudio table for sentence audio variants."""

import peewee as pw
from peewee_migrate import Migrator
from playhouse.postgres_ext import JSONField


def migrate(migrator: Migrator, database: pw.Database, **kwargs):
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

    class Sentence(BaseModel):
        class Meta:
            table_name = "sentence"

    class SentenceAudio(BaseModel):
        sentence = pw.ForeignKeyField(Sentence, backref="audio_variants")
        provider = pw.CharField(default="elevenlabs")
        audio_data = pw.BlobField()
        metadata = JSONField()
        created_by = pw.ForeignKeyField(AuthUser, null=True, backref="sentence_audio")

        class Meta:
            table_name = "sentenceaudio"

    with database.atomic():
        migrator.create_model(SentenceAudio)
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS sentenceaudio_sentence_id_idx ON sentenceaudio (sentence_id)"
        )
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS sentenceaudio_sentence_id_created_at_idx ON sentenceaudio (sentence_id, created_at)"
        )
        migrator.sql(
            "ALTER TABLE sentenceaudio DROP CONSTRAINT IF EXISTS sentenceaudio_sentence_id_fkey"
        )
        migrator.sql(
            "ALTER TABLE sentenceaudio ADD CONSTRAINT sentenceaudio_sentence_id_fkey FOREIGN KEY (sentence_id) REFERENCES sentence(id) ON DELETE CASCADE"
        )
        migrator.sql(
            "ALTER TABLE sentenceaudio DROP CONSTRAINT IF EXISTS fk_sentenceaudio_created_by_id"
        )
        migrator.sql(
            """
            ALTER TABLE "sentenceaudio"
            ADD CONSTRAINT fk_sentenceaudio_created_by_id
            FOREIGN KEY ("created_by_id")
            REFERENCES "auth"."users" ("id")
            ON DELETE CASCADE;
            """
        )


def rollback(migrator: Migrator, database: pw.Database, **kwargs):
    class SentenceAudio(pw.Model):
        class Meta:
            table_name = "sentenceaudio"

    with database.atomic():
        migrator.remove_model(SentenceAudio, cascade=True)
