"""Migration to move example sentences from JSON field to proper models."""

from peewee import CharField, TextField, ForeignKeyField, BlobField, Model
from playhouse.postgres_ext import JSONField

from api.db_models import BaseModel, Lemma


# Local model definitions matching schema at this migration point
class Sentence(BaseModel):
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    sentence = TextField()  # the actual sentence text
    translation = TextField()  # English translation
    audio_data = BlobField(null=True)  # MP3 audio data for the sentence
    lemma_words = JSONField()  # List of lemma words

    class Meta:
        table_name = "sentence"


class LemmaExampleSentence(BaseModel):
    lemma = ForeignKeyField(Lemma, backref="example_sentences", on_delete="CASCADE")
    sentence = ForeignKeyField(Sentence, backref="lemma_examples", on_delete="CASCADE")

    class Meta:
        table_name = "lemmaexamplesentence"
        indexes = ((("lemma", "sentence"), True),)  # Unique index


def migrate(migrator, database, fake=False, **kwargs):
    """Move example sentences from JSON field to proper models."""

    # Bind models to the database
    models = [Lemma, Sentence, LemmaExampleSentence]
    with database.bind_ctx(models):
        with database.atomic():
            # Get all lemmas with example sentences using a direct query
            lemmas = list(Lemma.select().where(Lemma.example_usage.is_null(False)))

            for lemma in lemmas:
                if not lemma.example_usage:
                    continue

                # Create Sentence and LemmaExampleSentence records for each example
                for example in lemma.example_usage:
                    # Skip if missing required fields
                    if not example.get("phrase") or not example.get("translation"):
                        continue

                    # Create the sentence
                    sentence, created = Sentence.get_or_create(
                        language_code=lemma.language_code,
                        sentence=example["phrase"],
                        translation=example["translation"],
                        defaults={
                            "lemma_words": [
                                lemma.lemma
                            ],  # Initialize with just this lemma
                        },
                    )

                    # Create the link
                    LemmaExampleSentence.get_or_create(lemma=lemma, sentence=sentence)

            # Clear the JSON field since data is now in proper models
            # Use SQL directly for consistency
            database.execute_sql(
                "UPDATE lemma SET example_usage = NULL WHERE example_usage IS NOT NULL"
            )


def rollback(migrator, database, fake=False, **kwargs):
    """Revert the migration by rebuilding the JSON field from the proper models."""

    # Bind models to the database
    models = [Lemma, Sentence, LemmaExampleSentence]
    with database.bind_ctx(models):
        with database.atomic():
            # For each lemma with example sentences
            for lemma_model in Lemma.select():
                # Get all sentences for this lemma
                example_sentences = []
                for link in lemma_model.example_sentences:
                    example_sentences.append(
                        {
                            "phrase": link.sentence.sentence,
                            "translation": link.sentence.translation,
                        }
                    )

                if example_sentences:
                    # Update the lemma's example_usage field directly
                    lemma_model.example_usage = example_sentences
                    lemma_model.save()
