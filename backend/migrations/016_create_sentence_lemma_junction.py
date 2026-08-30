"""Migration to create SentenceLemma junction table and migrate data from lemma_words JSONField."""

from peewee import BooleanField, CharField, TextField, ForeignKeyField, Model
from playhouse.postgres_ext import JSONField

from db_models import BaseModel


# Local model definitions matching schema at this migration point.
# Both are redefined here rather than imported from db_models: the live models have
# since been renamed language_code -> target_language_code (migration 030) and
# Sentence.lemma_words was dropped (migration 017), so importing them would emit SQL
# against columns that do not exist yet.
class Lemma(BaseModel):
    lemma = CharField()
    language_code = CharField()
    part_of_speech = CharField()
    translations = JSONField()
    # Migration 005 added is_complete as NOT NULL with no database default, so the
    # get_or_create below would hit a not-null violation without it declared here.
    is_complete = BooleanField(default=False)

    class Meta:
        table_name = "lemma"


class Sentence(BaseModel):
    language_code = CharField()
    sentence = TextField()
    translation = TextField()
    lemma_words = JSONField()

    class Meta:
        table_name = "sentence"


def migrate(migrator, database, fake=False, **kwargs):
    """Create SentenceLemma junction table and migrate data."""

    # First create the SentenceLemma model for the migration
    class SentenceLemma(BaseModel):
        sentence = ForeignKeyField(Sentence, backref="lemmas", on_delete="CASCADE")
        lemma = ForeignKeyField(Lemma, backref="sentences", on_delete="CASCADE")

        class Meta:
            indexes = ((("sentence", "lemma"), True),)  # Unique index

    # Bind models to the database
    models = [Lemma, Sentence, SentenceLemma]
    with database.bind_ctx(models):
        with database.atomic():
            # Create the new table
            SentenceLemma.create_table()

            # Get all sentences
            sentences = list(Sentence.select())

            print(f"Found {len(sentences)} sentences")

            # For each sentence, create SentenceLemma entries
            for sentence in sentences:
                if not sentence.lemma_words:
                    continue

                for lemma_word in sentence.lemma_words:
                    # Get or create the lemma
                    lemma, created = Lemma.get_or_create(
                        lemma=lemma_word,
                        language_code=sentence.language_code,
                        defaults={
                            "part_of_speech": "unknown",
                            "translations": [],
                        },
                    )

                    # Create the junction table entry
                    SentenceLemma.get_or_create(
                        sentence=sentence,
                        lemma=lemma,
                    )


def rollback(migrator, database, fake=False, **kwargs):
    """Rollback the changes."""

    # Drop the junction table. Done as raw SQL rather than via a model: BaseModel's
    # database is unset here, so a bare SentenceLemma.drop_table() raises
    # ImproperlyConfigured before it can drop anything.
    migrator.sql("DROP TABLE IF EXISTS sentencelemma;")
