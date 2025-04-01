"""Initial database schema."""

from peewee import (
    Model,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
    FloatField,
    BlobField,
    IntegerField,
    ForeignKeyField,
)


def migrate(migrator, database, *, fake=False):
    """Create initial schema."""
    if fake:
        return

    # Define models
    class BaseModel(Model):
        created_at = DateTimeField()
        updated_at = DateTimeField()

    class Lemma(BaseModel):
        lemma = CharField()
        language_code = CharField()
        part_of_speech = CharField(default="unknown")
        translations = TextField()  # JSON
        etymology = TextField(null=True)
        synonyms = TextField(null=True)  # JSON
        antonyms = TextField(null=True)  # JSON
        related_words_phrases_idioms = TextField(null=True)  # JSON
        register = CharField(null=True)
        commonality = FloatField(null=True)
        guessability = FloatField(null=True)
        cultural_context = TextField(null=True)
        mnemonics = TextField(null=True)  # JSON
        easily_confused_with = TextField(null=True)  # JSON
        example_usage = TextField(null=True)  # JSON

        class Meta:
            indexes = ((("lemma", "language_code"), True),)

    class Wordform(BaseModel):
        wordform = CharField(null=True)
        lemma_entry = ForeignKeyField(
            Lemma, backref="wordforms", null=True, on_delete="CASCADE"
        )
        language_code = CharField()
        part_of_speech = CharField(null=True)
        translations = TextField(null=True)  # JSON
        inflection_type = CharField(null=True)
        possible_misspellings = TextField(null=True)  # JSON
        is_lemma = BooleanField(default=False)

        class Meta:
            indexes = ((("wordform", "language_code"), True),)

    class Sentence(BaseModel):
        language_code = CharField()
        sentence = TextField()
        translation = TextField()
        lemma_words = TextField()  # JSON

        class Meta:
            indexes = ((("sentence", "language_code"), True),)

    class Phrase(BaseModel):
        language_code = CharField()
        canonical_form = CharField()
        raw_forms = TextField()  # JSON
        translations = TextField()  # JSON
        part_of_speech = CharField()
        register = CharField(null=True)
        commonality = FloatField(null=True)
        guessability = FloatField(null=True)
        etymology = TextField(null=True)
        cultural_context = TextField(null=True)
        mnemonics = TextField(null=True)  # JSON
        component_words = TextField(null=True)  # JSON
        usage_notes = TextField(null=True)
        difficulty_level = CharField(null=True)

        class Meta:
            indexes = ((("canonical_form", "language_code"), True),)

    class LemmaExampleSentence(BaseModel):
        lemma = ForeignKeyField(Lemma, backref="example_sentences", on_delete="CASCADE")
        sentence = ForeignKeyField(
            Sentence, backref="lemma_examples", on_delete="CASCADE"
        )

        class Meta:
            indexes = ((("lemma", "sentence"), True),)

    class PhraseExampleSentence(BaseModel):
        phrase = ForeignKeyField(
            Phrase, backref="example_sentences", on_delete="CASCADE"
        )
        sentence = ForeignKeyField(
            Sentence, backref="phrase_examples", on_delete="CASCADE"
        )
        context = TextField(null=True)

        class Meta:
            indexes = ((("phrase", "sentence"), True),)

    class RelatedPhrase(BaseModel):
        from_phrase = ForeignKeyField(Phrase, backref="related_to", on_delete="CASCADE")
        to_phrase = ForeignKeyField(Phrase, backref="related_from", on_delete="CASCADE")
        relationship_type = CharField()

        class Meta:
            indexes = ((("from_phrase", "to_phrase"), True),)

    class Sourcedir(BaseModel):
        path = CharField(unique=True)

        class Meta:
            indexes = ((("path",), True),)

    class Sourcefile(BaseModel):
        sourcedir = ForeignKeyField(
            Sourcedir, backref="sourcefiles", on_delete="CASCADE"
        )
        filename = CharField()
        image_data = BlobField(null=True)
        audio_data = BlobField(null=True)
        text_target = TextField()
        text_english = TextField()
        audio_filename = CharField(null=True)
        metadata = TextField()  # JSON

        class Meta:
            indexes = ((("sourcedir", "filename"), True),)

    class SourcefileWordform(BaseModel):
        sourcefile = ForeignKeyField(
            Sourcefile, backref="wordform_entries", on_delete="CASCADE"
        )
        wordform = ForeignKeyField(
            Wordform, backref="sourcefile_entries", on_delete="CASCADE"
        )
        centrality = FloatField()
        ordering = IntegerField(null=True)

        class Meta:
            indexes = ((("sourcefile", "wordform"), True),)

    # Create all tables using migrator
    migrator.create_model(Lemma)
    migrator.create_model(Wordform)
    migrator.create_model(Sentence)
    migrator.create_model(Phrase)
    migrator.create_model(LemmaExampleSentence)
    migrator.create_model(PhraseExampleSentence)
    migrator.create_model(RelatedPhrase)
    migrator.create_model(Sourcedir)
    migrator.create_model(Sourcefile)
    migrator.create_model(SourcefileWordform)


def rollback(migrator, database, *, fake=False):
    """Rollback the migration."""
    if fake:
        return

    migrator.drop_table("sourcefile_wordform")
    migrator.drop_table("sourcefile")
    migrator.drop_table("sourcedir")
    migrator.drop_table("related_phrase")
    migrator.drop_table("phrase_example_sentence")
    migrator.drop_table("lemma_example_sentence")
    migrator.drop_table("phrase")
    migrator.drop_table("sentence")
    migrator.drop_table("wordform")
    migrator.drop_table("lemma")
