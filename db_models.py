from peewee import (
    Model,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
    FloatField,
    BlobField,
    IntegerField,
    fn,
    DoesNotExist,
    ForeignKeyField,
)
from playhouse.postgres_ext import JSONField
from datetime import datetime
from typing import Optional
from slugify import slugify

from utils.db_connection import database
from config import (
    SOURCEDIR_SLUG_MAX_LENGTH,
    SOURCEFILE_SLUG_MAX_LENGTH,
    VALID_SOURCEFILE_TYPES,
)


class BaseModel(Model):
    """Base model class that should be used for all models."""

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        database = database

    @classmethod
    def update_or_create(cls, lookup: dict, updates: dict):
        """
        Implementation of update-or-create pattern that explicitly separates
        lookup vs update fields.

        Args:
            lookup: Fields used for existence check (should have unique constraint)
            updates: Fields to update/create

        Returns:
            Tuple of (instance, created)
        """
        # Validate that lookup fields have unique constraint
        if not any(
            index[1]  # index[1] is unique flag
            and set(lookup.keys()).issubset(set(index[0]))
            for index in cls._meta.indexes  # type: ignore
        ):
            raise ValueError("Lookup fields must be covered by a unique constraint")

        with cls._meta.database.atomic():  # type: ignore
            try:
                # Try to get existing record
                instance = cls.get(**lookup)
                if updates:
                    for field, value in updates.items():
                        setattr(instance, field, value)
                    instance.save()
                return instance, False
            except cls.DoesNotExist:  # type: ignore
                # Create new record with combined lookup and updates
                return cls.create(**lookup, **updates), True


class Lemma(BaseModel):
    lemma = CharField()  # the dictionary form
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    part_of_speech = CharField(default="unknown")  # e.g. "verb", "adjective", "noun"
    translations = JSONField(default=list)  # list[str] of English translations
    etymology = TextField(null=True)  # origins and development of the word
    synonyms = JSONField(null=True)  # list[dict] with lemma and translation
    antonyms = JSONField(null=True)  # list[dict] with lemma and translation
    related_words_phrases_idioms = JSONField(
        null=True
    )  # list[dict] with lemma and translation
    register = CharField(null=True)  # e.g. "neutral", "formal", "informal"
    commonality = FloatField(null=True)  # from 0-1, how common in regular use
    guessability = FloatField(
        null=True
    )  # from 0-1, how easy to guess for English speaker
    cultural_context = TextField(null=True)  # usage in cultural context
    mnemonics = JSONField(null=True)  # list[str] of memory aids
    easily_confused_with = JSONField(
        null=True
    )  # list[dict] with detailed confusion info
    example_usage = JSONField(null=True)  # list[dict] with phrase and translation
    is_complete = BooleanField(default=False)  # whether all metadata has been populated

    class Meta:
        indexes = ((("lemma", "language_code"), True),)  # Unique index

    @staticmethod
    def check_metadata_completeness(metadata: dict) -> bool:
        """Check if metadata has all required fields with non-empty values.

        Args:
            metadata: Dictionary containing lemma metadata

        Returns:
            bool: True if all required fields are present and non-empty
        """
        return metadata["is_complete"]

    @staticmethod
    def _sanitize_easily_confused_entry(entry: dict) -> dict:
        """Ensure each easily_confused_with entry has all required fields."""
        if not entry:
            return {}

        # Handle case where entry is a string
        if isinstance(entry, str):
            return {
                "lemma": entry,
                "explanation": "",
                "example_usage_this_target": "",
                "example_usage_this_source": "",
                "example_usage_other_target": "",
                "example_usage_other_source": "",
                "mnemonic": "",
                "notes": "",
            }

        required_fields = {
            "lemma": "",
            "explanation": "",
            "example_usage_this_target": "",
            "example_usage_this_source": "",
            "example_usage_other_target": "",
            "example_usage_other_source": "",
            "mnemonic": "",
            "notes": "",
        }

        return {**required_fields, **entry}

    def to_dict(self) -> dict:
        """Convert lemma model to dictionary format matching the old metadata schema."""
        data = {
            "lemma": self.lemma,
            "is_complete": self.is_complete,
            "part_of_speech": self.part_of_speech,
            "translations": self.translations or [],
            "etymology": self.etymology,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "related_words_phrases_idioms": self.related_words_phrases_idioms,
            "register": self.register,
            "commonality": self.commonality,
            "guessability": self.guessability,
            "cultural_context": self.cultural_context,
            "mnemonics": self.mnemonics,
            "example_usage": [
                {
                    "phrase": es.sentence.sentence,
                    "translation": es.sentence.translation,
                    "slug": es.sentence.slug,
                }
                for es in self.example_sentences  # type: ignore
            ],
            "example_wordforms": [wf.wordform for wf in self.wordforms],  # type: ignore
        }

        # Preserve None for easily_confused_with if not set
        if self.easily_confused_with is not None:
            data["easily_confused_with"] = [
                self._sanitize_easily_confused_entry(entry)
                for entry in self.easily_confused_with
            ]
        else:
            data["easily_confused_with"] = None

        return data

    @classmethod
    def get_all_for_language(cls, language_code: str, sort_by: str = "alpha"):
        """Get all lemmas for a language with specified sorting."""
        query = cls.select().where(cls.language_code == language_code)

        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        else:
            query = query.order_by(cls.lemma)

        return query

    def get_all_wordforms(self) -> set[str]:
        """Get a flat set of all known forms of this lemma."""
        forms = set()

        # Add the lemma itself
        forms.add(self.lemma)

        # Add all related wordforms from the database
        forms.update(wf.wordform for wf in self.wordforms)  # type: ignore

        # Add related forms from metadata
        if self.related_words_phrases_idioms:
            forms.update(
                related["lemma"]
                for related in self.related_words_phrases_idioms
                if isinstance(related, dict)
                and "lemma" in related
                and " " not in related["lemma"]
            )

        return forms


class Wordform(BaseModel):
    wordform = CharField(null=True)  # the sanitized form if valid, None if invalid
    lemma_entry = ForeignKeyField(
        Lemma, backref="wordforms", null=True, on_delete="CASCADE"
    )  # reference to the lemma entry
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    part_of_speech = CharField(null=True)  # e.g. "verb", "adjective", "noun"
    translations = JSONField(null=True)  # List of English translations
    inflection_type = CharField(null=True)  # e.g. "first-person singular present"
    possible_misspellings = JSONField(null=True)  # List of suggested corrections
    is_lemma = BooleanField(default=False)  # whether this is a dictionary form

    class Meta:
        indexes = ((("wordform", "language_code"), True),)  # Unique index

    @classmethod
    def get_or_create_from_metadata(
        cls,
        wordform: str,
        language_code: str,
        metadata: dict,
        lemma_entry: Optional[Lemma] = None,
    ):
        """Get or create a wordform entry from metadata.

        Args:
            wordform: The wordform text
            language_code: The language code (e.g. 'el' for Greek)
            metadata: Dictionary containing wordform metadata
            lemma_entry: Optional pre-fetched lemma model

        Returns:
            Tuple of (wordform_model, created)
        """
        # If no lemma provided but metadata has lemma info, get/create the lemma
        if not lemma_entry and metadata.get("lemma"):
            # Remove fields that are in lookup from metadata
            lemma_metadata = metadata.copy()
            lemma_lookup = {
                "lemma": metadata["lemma"],
                "language_code": language_code,
            }
            for key in lemma_lookup:
                if key in lemma_metadata:
                    del lemma_metadata[key]

            lemma_entry, _ = Lemma.update_or_create(
                lookup=lemma_lookup,
                updates=lemma_metadata,
            )

        updates = {
            "lemma_entry": lemma_entry,
            "part_of_speech": metadata.get("part_of_speech"),
            "translations": metadata.get("translations", []),
            "inflection_type": metadata.get("inflection_type"),
            "possible_misspellings": metadata.get("possible_misspellings"),
            "is_lemma": metadata.get("is_lemma", False),
        }

        return cls.update_or_create(
            lookup={"wordform": wordform, "language_code": language_code},
            updates=updates,
        )

    def to_dict(self) -> dict:
        """Convert wordform model to dictionary format matching the old metadata schema."""
        return {
            "wordform": self.wordform,
            "lemma": self.lemma_entry.lemma if self.lemma_entry else None,
            "part_of_speech": self.part_of_speech,
            "translations": self.translations or [],
            "inflection_type": self.inflection_type,
            "possible_misspellings": self.possible_misspellings,
            "is_lemma": self.is_lemma,
        }

    @classmethod
    def find_by_text(cls, wordform: str, language_code: str) -> Optional["Wordform"]:
        """Find a wordform by its text, case-insensitive."""
        try:
            return cls.get(
                fn.Lower(cls.wordform) == wordform.lower(),
                cls.language_code == language_code,
            )
        except DoesNotExist:
            return None

    @classmethod
    def get_all_for_language(cls, language_code: str, sort_by: str = "alpha"):
        """Get all wordforms for a language with specified sorting."""
        query = cls.select().where(cls.language_code == language_code)

        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        else:
            query = query.order_by(cls.wordform)

        return query


class Sentence(BaseModel):
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    sentence = TextField()  # the actual sentence text
    translation = TextField()  # English translation
    audio_data = BlobField(null=True)  # MP3 audio data for the sentence
    slug = CharField(max_length=255)  # URL-friendly version of the sentence

    def save(self, *args, **kwargs):
        # Generate slug from sentence if not set
        if not self.slug:
            self.slug = slugify(str(self.sentence))
            # Truncate slug if it exceeds max length
            if len(self.slug) > 255:
                self.slug = self.slug[:255]
        return super().save(*args, **kwargs)

    @property
    def lemma_words(self) -> list[str]:
        """For backwards compatibility, return list of lemma words."""
        return [sl.lemma.lemma for sl in self.lemmas]  # type: ignore

    class Meta:
        indexes = (
            (("sentence", "language_code"), True),  # Unique index
            (("slug", "language_code"), True),  # Unique index for URLs
        )


class SentenceLemma(BaseModel):
    """Junction table between Sentence and Lemma."""

    sentence = ForeignKeyField(Sentence, backref="lemmas", on_delete="CASCADE")
    lemma = ForeignKeyField(Lemma, backref="sentences", on_delete="CASCADE")

    class Meta:
        indexes = ((("sentence", "lemma"), True),)  # Unique index


class Phrase(BaseModel):
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    canonical_form = CharField()  # the standard form of the phrase
    raw_forms = JSONField()  # list[str] of alternative forms
    translations = JSONField()  # list[str] of English translations
    part_of_speech = CharField()  # e.g. "verbal phrase"
    register = CharField(null=True)  # e.g. "informal"
    commonality = FloatField(null=True)  # from 0-1, how common in regular use
    guessability = FloatField(
        null=True
    )  # from 0-1, how easy to guess for English speaker
    etymology = TextField(null=True)  # origins and development
    cultural_context = TextField(null=True)  # cultural usage context
    mnemonics = JSONField(null=True)  # list[str] of memory aids
    component_words = JSONField(null=True)  # list[dict] with lemma, translation, notes
    usage_notes = TextField(null=True)  # general notes about usage
    difficulty_level = CharField(null=True)  # e.g. "intermediate"

    class Meta:
        indexes = ((("canonical_form", "language_code"), True),)  # Unique index

    def to_dict(self) -> dict:
        """Convert phrase model to dictionary format."""
        return {
            "canonical_form": self.canonical_form,
            "raw_forms": self.raw_forms or [],
            "translations": self.translations or [],
            "part_of_speech": self.part_of_speech,
            "register": self.register,
            "commonality": self.commonality,
            "guessability": self.guessability,
            "etymology": self.etymology,
            "cultural_context": self.cultural_context,
            "mnemonics": self.mnemonics,
            "component_words": self.component_words,
            "usage_notes": self.usage_notes,
            "difficulty_level": self.difficulty_level,
        }

    @classmethod
    def get_all_for_language(cls, language_code: str, sort_by: str = "alpha"):
        """Get all phrases for a language with specified sorting."""
        query = cls.select().where(cls.language_code == language_code)

        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        else:
            query = query.order_by(cls.canonical_form)

        return query


class LemmaExampleSentence(BaseModel):
    lemma = ForeignKeyField(Lemma, backref="example_sentences", on_delete="CASCADE")
    sentence = ForeignKeyField(Sentence, backref="lemma_examples", on_delete="CASCADE")

    class Meta:
        indexes = ((("lemma", "sentence"), True),)  # Unique index


class PhraseExampleSentence(BaseModel):
    phrase = ForeignKeyField(Phrase, backref="example_sentences", on_delete="CASCADE")
    sentence = ForeignKeyField(Sentence, backref="phrase_examples", on_delete="CASCADE")
    context = TextField(
        null=True
    )  # Optional context about how the phrase is used in this sentence

    class Meta:
        indexes = ((("phrase", "sentence"), True),)  # Unique index


class RelatedPhrase(BaseModel):
    from_phrase = ForeignKeyField(Phrase, backref="related_to", on_delete="CASCADE")
    to_phrase = ForeignKeyField(Phrase, backref="related_from", on_delete="CASCADE")
    relationship_type = CharField()  # e.g. "similar meaning", "opposite", etc.

    class Meta:
        indexes = ((("from_phrase", "to_phrase"), True),)  # Unique index


class Sourcedir(BaseModel):
    path = CharField()  # the directory path
    language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    slug = CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH)

    def save(self, *args, **kwargs):
        # Generate slug from path if not set
        if not self.slug:
            self.slug = slugify(str(self.path))
            # Truncate slug if it exceeds max length
            if len(self.slug) > SOURCEDIR_SLUG_MAX_LENGTH:
                self.slug = self.slug[:SOURCEDIR_SLUG_MAX_LENGTH]
        return super().save(*args, **kwargs)

    class Meta:
        database = database
        indexes = (
            (("path", "language_code"), True),  # Unique index
            (("slug", "language_code"), True),  # Unique index for URLs
        )


class Sourcefile(BaseModel):
    sourcedir = ForeignKeyField(Sourcedir, backref="sourcefiles", on_delete="CASCADE")
    filename = CharField()  # just the filename part
    image_data = BlobField(null=True)  # the original image
    audio_data = BlobField(null=True)  # optional mp3 audio
    text_target = TextField()  # the source text in target language
    text_english = TextField()  # the English translation
    audio_filename = CharField(null=True)  # optional reference to mp3 file
    metadata = JSONField()  # remaining metadata (words, phrases, etc.)
    slug = CharField(max_length=SOURCEFILE_SLUG_MAX_LENGTH)
    sourcefile_type = (
        CharField()
    )  # Type of source: "text" for direct text input, "image" for uploaded images, "audio" for audio files, "youtube_audio" for YouTube audio downloads

    def save(self, *args, **kwargs):
        # Always generate slug from current filename
        self.slug = slugify(str(self.filename))
        # Validate sourcefile_type
        if self.sourcefile_type not in VALID_SOURCEFILE_TYPES:
            raise ValueError(
                f"Invalid sourcefile_type: {self.sourcefile_type}. "
                f"Must be one of: {', '.join(sorted(VALID_SOURCEFILE_TYPES))}"
            )
        return super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (("sourcedir", "filename"), True),  # Composite unique index
            (("sourcedir", "slug"), True),  # Unique slug per sourcedir
        )


class SourcefileWordform(BaseModel):
    sourcefile = ForeignKeyField(
        Sourcefile, backref="wordform_entries", on_delete="CASCADE"
    )
    wordform = ForeignKeyField(
        Wordform, backref="sourcefile_entries", on_delete="CASCADE"
    )
    centrality = FloatField(
        null=True
    )  # from 0-1 if set by LLM during initial processing, NULL if word was auto-discovered later
    ordering = IntegerField(null=True)  # optional display ordering

    class Meta:
        indexes = ((("sourcefile", "wordform"), True),)  # Unique index


class SourcefilePhrase(BaseModel):
    sourcefile = ForeignKeyField(
        Sourcefile, backref="phrase_entries", on_delete="CASCADE"
    )
    phrase = ForeignKeyField(Phrase, backref="sourcefile_entries", on_delete="CASCADE")
    centrality = FloatField(
        null=True
    )  # from 0-1 indicating importance of phrase in the sourcefile
    ordering = IntegerField(null=True)  # display order in the sourcefile

    class Meta:
        indexes = ((("sourcefile", "phrase"), True),)  # Unique index


def get_models():
    """Return all models for database initialization"""
    return [
        Lemma,
        Wordform,
        Sentence,
        SentenceLemma,
        Phrase,
        LemmaExampleSentence,
        PhraseExampleSentence,
        RelatedPhrase,
        Sourcedir,
        Sourcefile,
        SourcefileWordform,
        SourcefilePhrase,
    ]  # Order matters for foreign key dependencies
