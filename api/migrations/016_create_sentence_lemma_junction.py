"""Migration to create SentenceLemma junction table and migrate data from lemma_words JSONField."""

from peewee import CharField, TextField, ForeignKeyField, Model
from playhouse.postgres_ext import JSONField

from api.db_models import BaseModel, Lemma, Sentence


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

    # Create the SentenceLemma model for the rollback
    class SentenceLemma(BaseModel):
        sentence = ForeignKeyField(Sentence, backref="lemmas", on_delete="CASCADE")
        lemma = ForeignKeyField(Lemma, backref="sentences", on_delete="CASCADE")

        class Meta:
            table_name = "sentencelemma"

    # Drop the junction table
    SentenceLemma.drop_table()
