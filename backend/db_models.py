from peewee import (
    Model,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
    FloatField,
    BlobField,
    IntegerField,
    JOIN,
    fn,
    DoesNotExist,
    ForeignKeyField,
    UUIDField,
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


class AuthUser(Model):
    """Model to reference Supabase auth.users table."""

    id = UUIDField(primary_key=True)

    class Meta:
        database = database
        table_name = "users"
        schema = "auth"


class BaseModel(Model):
    """Base model class that should be used for all models."""

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()

        # Check if this is a new instance (not yet in the database)
        is_new = self.get_id() is None  # _pk is None for new instances

        # Only for new instances, try to set created_by from Flask g object if field exists
        if (
            is_new
            and hasattr(self, "created_by")
            and not getattr(self, "created_by", None)
        ):
            try:
                # Import Flask's g object within the method to avoid circular imports
                from flask import g

                # Check if g has user_id and set it on the model
                if hasattr(g, "user_id") and g.user_id:
                    self.created_by = g.user_id
            except (ImportError, RuntimeError):
                # Flask context might not be available (e.g., in scripts, tests)
                pass

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
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
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
    language_level = CharField(null=True)  # e.g. "A1", "B2", "C1"
    created_by = ForeignKeyField(
        AuthUser, backref="lemmas", null=True, on_delete="CASCADE"
    )

    class Meta:
        indexes = ((("lemma", "target_language_code"), True),)  # Unique index

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
            "language_level": self.language_level,  # Include CEFR language level
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
    def get_all_lemmas_for(
        cls,
        target_language_code: str,
        sourcedir=None,
        sourcefile=None,
        sort_by: str = "alpha",
    ):
        """Get lemmas for a language with specified sorting, optionally filtered by sourcedir or sourcefile.

        Args:
            target_language_code: 2-letter language code (e.g. "el" for Greek)
            sourcedir: Optional Sourcedir object to filter by
            sourcefile: Optional Sourcefile object to filter by
            sort_by: Sorting method ("alpha", "date", or "commonality")

        Returns:
            Optimized query of lemmas matching the criteria
        """
        # Start with a base query
        if sourcefile:
            # Filter by specific sourcefile
            query = (
                cls.select(cls)
                .distinct()
                .join(Wordform, on=(Wordform.lemma_entry == cls.id))  # type: ignore
                .join(
                    SourcefileWordform, on=(SourcefileWordform.wordform == Wordform.id)  # type: ignore
                )
                .where(
                    (cls.target_language_code == target_language_code)
                    & (SourcefileWordform.sourcefile == sourcefile)
                )
            )
        elif sourcedir:
            # Filter by sourcedir
            query = (
                cls.select(cls)
                .distinct()
                .join(Wordform, on=(Wordform.lemma_entry == cls.id))  # type: ignore
                .join(
                    SourcefileWordform, on=(SourcefileWordform.wordform == Wordform.id)  # type: ignore
                )
                .join(Sourcefile, on=(SourcefileWordform.sourcefile == Sourcefile.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (Sourcefile.sourcedir == sourcedir)
                )
            )
        else:
            # No filter, get all lemmas for the language
            query = cls.select().where(cls.target_language_code == target_language_code)

        # Apply sorting
        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        elif sort_by == "commonality":
            # Sort by commonality (highest first), then alphabetically for ties
            query = query.order_by(
                fn.COALESCE(cls.commonality, 0.0).desc(), fn.Lower(cls.lemma)
            )
        else:
            # Default alpha sorting
            query = query.order_by(fn.Lower(cls.lemma))

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
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    part_of_speech = CharField(null=True)  # e.g. "verb", "adjective", "noun"
    translations = JSONField(null=True)  # List of English translations
    inflection_type = CharField(null=True)  # e.g. "first-person singular present"
    possible_misspellings = JSONField(null=True)  # List of suggested corrections
    is_lemma = BooleanField(default=False)  # whether this is a dictionary form
    created_by = ForeignKeyField(
        AuthUser,
        backref="wordforms",
        null=True,
        on_delete="CASCADE",
    )

    class Meta:
        indexes = ((("wordform", "target_language_code"), True),)  # Unique index

    def save(self, *args, **kwargs):
        """Override save to ensure wordform is in NFC form."""
        # Import here to avoid circular imports
        import unicodedata

        # Ensure wordform is in NFC form if it exists
        if self.wordform is not None:
            # Convert to string first to ensure compatibility with unicodedata.normalize
            self.wordform = unicodedata.normalize("NFC", str(self.wordform))

        # Call parent save method
        return super().save(*args, **kwargs)

    @classmethod
    def get_or_create_from_metadata(
        cls,
        wordform: str,
        target_language_code: str,
        metadata: dict,
        lemma_entry: Optional[Lemma] = None,
    ):
        """Get or create a wordform entry from metadata.

        Args:
            wordform: The wordform text
            target_language_code: The language code (e.g. 'el' for Greek)
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
                "target_language_code": target_language_code,
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
            lookup={
                "wordform": wordform,
                "target_language_code": target_language_code,
            },
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
    def find_by_text(
        cls, wordform: str, target_language_code: str
    ) -> Optional["Wordform"]:
        """Find a wordform by its text, case-insensitive."""
        try:
            return cls.get(
                fn.Lower(cls.wordform) == wordform.lower(),
                cls.target_language_code == target_language_code,
            )
        except DoesNotExist:
            return None

    @classmethod
    def get_all_wordforms_for(
        cls,
        target_language_code: str,
        sourcedir=None,
        sourcefile=None,
        sort_by: str = "alpha",
        include_junction_data: bool = False,
    ):
        """Get wordforms for a language with specified sorting, optionally filtered by sourcedir or sourcefile.

        Args:
            target_language_code: 2-letter language code (e.g. "el" for Greek)
            sourcedir: Optional Sourcedir object or slug to filter by
            sourcefile: Optional Sourcefile object to filter by
            sort_by: Sorting method ("alpha", "date", or "commonality")
            include_junction_data: Whether to include junction table data in the result for sourcefile queries

        Returns:
            If sourcefile is provided:
              List of dictionaries containing wordform data with centrality and ordering fields added
            Otherwise:
              Optimized query of wordforms matching the criteria
        """
        # Handle slug parameters for backwards compatibility
        sourcedir_slug = None

        # Check if parameters are objects or slugs
        if isinstance(sourcedir, str):
            sourcedir_slug = sourcedir
            sourcedir = None

        # Start with an optimized join query to get all related data
        if sourcefile:
            # Filter by specific sourcefile object and include junction data
            query = (
                cls.select(cls, Lemma, SourcefileWordform)
                .join(SourcefileWordform, on=(SourcefileWordform.wordform == cls.id))  # type: ignore
                .switch(cls)
                .join(Lemma, on=(cls.lemma_entry == Lemma.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (SourcefileWordform.sourcefile == sourcefile)
                )
                .order_by(SourcefileWordform.ordering)
            )

            # Run query and build custom result with junction data
            results = []
            for result in query:
                # Add junction data directly to wordform dict to avoid N+1 queries
                wordform_d = result.to_dict()
                wordform_d["centrality"] = result.sourcefilewordform.centrality
                wordform_d["ordering"] = result.sourcefilewordform.ordering
                results.append(wordform_d)
            return results
        elif sourcedir:
            # Filter by sourcedir object
            query = (
                cls.select(cls, Lemma)
                .join(SourcefileWordform, on=(SourcefileWordform.wordform == cls.id))  # type: ignore
                .join(Sourcefile, on=(SourcefileWordform.sourcefile == Sourcefile.id))  # type: ignore
                .switch(cls)
                .join(Lemma, on=(cls.lemma_entry == Lemma.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (Sourcefile.sourcedir == sourcedir)
                )
                .group_by(cls.id, Lemma.id)  # type: ignore
            )
        elif sourcedir_slug:
            # Filter by sourcedir slug
            query = (
                cls.select(cls, Lemma)
                .join(SourcefileWordform, on=(SourcefileWordform.wordform == cls.id))  # type: ignore
                .join(Sourcefile, on=(SourcefileWordform.sourcefile == Sourcefile.id))  # type: ignore
                .join(Sourcedir, on=(Sourcefile.sourcedir == Sourcedir.id))  # type: ignore
                .join(Lemma, on=(cls.lemma_entry == Lemma.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (Sourcedir.slug == sourcedir_slug)
                )
                .group_by(cls.id, Lemma.id)
            )
        else:
            # No filter, get all wordforms for the language
            query = (
                cls.select(cls, Lemma)
                .join(Lemma, on=(cls.lemma_entry == Lemma.id))  # type: ignore
                .where(cls.target_language_code == target_language_code)
            )

        # Apply sorting
        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        elif sort_by == "commonality":
            # For commonality sorting, order by lemma commonality (highest first)
            # Then alphabetically for ties
            query = query.order_by(
                fn.COALESCE(Lemma.commonality, 0).desc(), fn.Lower(cls.wordform)
            )
        else:
            # Default alpha sorting
            query = query.order_by(fn.Lower(cls.wordform))

        return query


class Sentence(BaseModel):
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    sentence = TextField()  # the actual sentence text
    translation = TextField()  # English translation
    audio_data = BlobField(null=True)  # MP3 audio data for the sentence
    slug = CharField(max_length=255)  # URL-friendly version of the sentence
    language_level = CharField(null=True)  # e.g. "A1", "B2", "C1"
    created_by = ForeignKeyField(
        AuthUser, backref="sentences", null=True, on_delete="CASCADE"
    )

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

    @classmethod
    def get_all_sentences_for(
        cls,
        target_language_code: str,
        sort_by: str = "date",
    ):
        """Get sentences for a language with efficient loading of related lemmas.

        Args:
            target_language_code: 2-letter language code
            sort_by: Sorting method ("date" or "alpha")

        Returns:
            List of sentence dictionaries with preloaded lemma data
        """
        # Start with a simple query for all sentences in this language
        query = cls.select().where(cls.target_language_code == target_language_code)

        # Apply sorting
        if sort_by == "date":
            query = query.order_by(fn.COALESCE(cls.updated_at, cls.created_at).desc())
        else:
            query = query.order_by(fn.Lower(cls.sentence))

        # Fetch sentences first
        sentences = list(query)

        # Then fetch all related lemma data in one bulk query
        lemma_data = {}
        if sentences:
            sentence_ids = [s.id for s in sentences]

            # Use a raw SQL query for the join to avoid ORM complexity
            # This gets all sentence-lemma relationships in one query
            lemma_query = (
                SentenceLemma.select(SentenceLemma.sentence, Lemma.lemma)
                .join(Lemma)
                .where(SentenceLemma.sentence.in_(sentence_ids))  # type: ignore
            )

            # Group lemmas by sentence id
            for sl in lemma_query:
                if sl.sentence_id not in lemma_data:
                    lemma_data[sl.sentence_id] = []
                lemma_data[sl.sentence_id].append(sl.lemma.lemma)

        # Convert to dictionary format with lemmas preloaded
        results = []
        for sentence in sentences:
            results.append(
                {
                    "id": sentence.id,
                    "sentence": sentence.sentence,
                    "translation": sentence.translation,
                    "lemma_words": lemma_data.get(sentence.id, []),
                    "target_language_code": sentence.target_language_code,
                    "slug": sentence.slug,
                    "has_audio": bool(sentence.audio_data),
                    "language_level": sentence.language_level,
                }
            )

        return results

    class Meta:
        indexes = (
            (("sentence", "target_language_code"), True),  # Unique index
            (("slug", "target_language_code"), True),  # Unique index for URLs
        )


class SentenceLemma(BaseModel):
    """Junction table between Sentence and Lemma."""

    sentence = ForeignKeyField(Sentence, backref="lemmas", on_delete="CASCADE")
    lemma = ForeignKeyField(Lemma, backref="sentences", on_delete="CASCADE")

    class Meta:
        indexes = ((("sentence", "lemma"), True),)  # Unique index


class Phrase(BaseModel):
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    canonical_form = CharField()  # the standard form of the phrase
    raw_forms = JSONField()  # list[str] of alternative forms
    translations = JSONField()  # list[str] of English translations
    literal_translation = TextField(
        null=True
    )  # word-for-word translation showing structure
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
    language_level = CharField(null=True)  # CEFR language level (e.g. "A1", "B2", "C1")
    slug = CharField(
        max_length=255, null=True
    )  # URL-friendly version of the canonical form
    created_by = ForeignKeyField(
        AuthUser, backref="phrases", null=True, on_delete="CASCADE"
    )

    def save(self, *args, **kwargs):
        # Generate slug from canonical_form if not set
        if not self.slug:
            self.slug = slugify(str(self.canonical_form))
            # Truncate slug if it exceeds max length
            if len(self.slug) > 255:
                self.slug = self.slug[:255]
        return super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (("canonical_form", "target_language_code"), True),  # Unique index
            (("slug", "target_language_code"), True),  # Unique index for URLs
        )

    def to_dict(self) -> dict:
        """Convert phrase model to dictionary format."""
        return {
            "canonical_form": self.canonical_form,
            "raw_forms": self.raw_forms or [],
            "translations": self.translations or [],
            "literal_translation": self.literal_translation,
            "part_of_speech": self.part_of_speech,
            "register": self.register,
            "commonality": self.commonality,
            "guessability": self.guessability,
            "etymology": self.etymology,
            "cultural_context": self.cultural_context,
            "mnemonics": self.mnemonics,
            "component_words": self.component_words,
            "usage_notes": self.usage_notes,
            "language_level": self.language_level,  # Include CEFR language level
            "slug": self.slug,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(self.created_at, datetime)
                else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(self.updated_at, datetime)
                else None
            ),
        }

    @classmethod
    def get_all_phrases_for(
        cls,
        target_language_code: str,
        sourcedir=None,
        sourcefile=None,
        sort_by: str = "alpha",
        include_junction_data: bool = False,
    ):
        """Get phrases for a language with specified sorting, optionally filtered by sourcedir or sourcefile.

        Args:
            target_language_code: 2-letter language code (e.g. "el" for Greek)
            sourcedir: Optional Sourcedir object or slug to filter by
            sourcefile: Optional Sourcefile object to filter by
            sort_by: Sorting method ("alpha" or "date")
            include_junction_data: Whether to include junction table data in the result for sourcefile queries

        Returns:
            If sourcefile is provided:
              List of phrase dictionaries with centrality and ordering fields added
            Otherwise:
              Optimized query of phrases matching the criteria
        """
        # Start with an optimized join query to get all related data
        if sourcefile:
            # Filter by specific sourcefile object and include junction data
            query = (
                cls.select(cls, SourcefilePhrase)
                .join(SourcefilePhrase, on=(SourcefilePhrase.phrase == cls.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (SourcefilePhrase.sourcefile == sourcefile)
                )
                .order_by(SourcefilePhrase.ordering)
            )

            # Process results to include junction data
            results = []
            for result in query:
                phrase_d = result.to_dict()
                # Add junction data directly to phrase dictionary
                phrase_d["centrality"] = result.sourcefilephrase.centrality
                phrase_d["ordering"] = result.sourcefilephrase.ordering
                results.append(phrase_d)
            return results
        elif sourcedir:
            # Filter by sourcedir object
            query = (
                cls.select(cls)
                .join(SourcefilePhrase, on=(SourcefilePhrase.phrase == cls.id))  # type: ignore
                .join(Sourcefile, on=(SourcefilePhrase.sourcefile == Sourcefile.id))  # type: ignore
                .where(
                    (cls.target_language_code == target_language_code)
                    & (Sourcefile.sourcedir == sourcedir)
                )
                .group_by(cls.id)  # type: ignore
            )
        else:
            # No filter, get all phrases for the language
            query = cls.select().where(cls.target_language_code == target_language_code)

        # Apply sorting
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
    path = CharField(max_length=1024)  # the directory path
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    slug = CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH)
    description = TextField(null=True)  # description of the directory content
    created_by = ForeignKeyField(
        AuthUser, backref="sourcedirs", null=True, on_delete="CASCADE"
    )

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
            (("path", "target_language_code"), True),  # Unique index
            (("slug", "target_language_code"), True),  # Unique index for URLs
        )


class Sourcefile(BaseModel):
    sourcedir = ForeignKeyField(Sourcedir, backref="sourcefiles", on_delete="CASCADE")
    filename = CharField(max_length=1024)  # just the filename part
    description = TextField(null=True)  # description of the file content
    image_data = BlobField(null=True)  # the original image
    audio_data = BlobField(null=True)  # optional mp3 audio
    text_target = TextField()  # the source text in target language
    text_english = TextField()  # the English translation
    audio_filename = CharField(
        max_length=1024, null=True
    )  # optional reference to mp3 file
    metadata = JSONField()  # remaining metadata (words, phrases, etc.)
    slug = CharField(max_length=SOURCEFILE_SLUG_MAX_LENGTH)
    sourcefile_type = (
        CharField()
    )  # Type of source: "text" for direct text input, "image" for uploaded images, "audio" for audio files, "youtube_audio" for YouTube audio downloads
    created_by = ForeignKeyField(
        AuthUser, backref="sourcefiles", null=True, on_delete="CASCADE"
    )
    publication_date = DateTimeField(null=True)  # original publication date if known
    num_words = IntegerField(null=True)  # number of words in the text
    language_level = CharField(null=True)  # e.g. "A1", "B2", "C1"
    url = CharField(max_length=2048, null=True)  # original source URL if applicable
    title_target = CharField(max_length=2048, null=True)  # title in target language
    ai_generated = BooleanField(default=False)  # whether this file was generated by AI

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


class Profile(BaseModel):
    """User profile linked to Supabase auth.users."""

    user_id = CharField(unique=True)  # References auth.users.id in Supabase
    target_language_code = CharField(null=True)  # User's preferred language
    # Removed email field as it should come directly from AuthUser (auth.users)

    class Meta:
        indexes = ((("user_id",), True),)  # Unique index

    def to_dict(self) -> dict:
        """Convert profile model to dictionary format."""
        return {
            "id": self.get_id(),
            "user_id": self.user_id,
            "target_language_code": self.target_language_code,
            "created_at": (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if isinstance(self.updated_at, datetime)
                else None
            ),
        }

    @classmethod
    def get_or_create_for_user(cls, user_id: str):
        """Get or create a profile for a Supabase auth user.

        Args:
            user_id: Supabase auth user ID

        Returns:
            Tuple of (profile, created)
        """
        try:
            profile = cls.get(cls.user_id == user_id)
            return profile, False
        except DoesNotExist:
            # Create new profile with default values
            profile = cls.create(user_id=user_id)
            return profile, True

    @classmethod
    def get_email_by_user_id(cls, user_id: str) -> Optional[str]:
        """Get a user's email by their user ID.

        DEPRECATED: Use AuthUser model to get email directly from auth.users

        Args:
            user_id: Supabase auth user ID

        Returns:
            The user's email if found, or None
        """
        try:
            # Try to get email from auth.users via AuthUser model
            auth_user = AuthUser.get_by_id(user_id)
            if hasattr(auth_user, "email"):
                return auth_user.email
            return None
        except DoesNotExist:
            return None


class UserLemma(BaseModel):
    """Junction table between auth.users and Lemma for tracking user-specific lemma preferences."""

    user_id = UUIDField()  # Reference to auth.users.id
    lemma = ForeignKeyField(Lemma, backref="user_lemmas", on_delete="CASCADE")
    ignored_dt = DateTimeField(
        null=True
    )  # When the lemma was ignored (NULL = not ignored)

    class Meta:
        indexes = ((("user_id", "lemma"), True),)  # Unique index
        table_name = "userlemma"

    @classmethod
    def ignore_lemma(cls, user_id: str, lemma: Lemma) -> "UserLemma":
        """Ignore a lemma for a user.

        Args:
            user_id: UUID of auth.users
            lemma: Lemma model

        Returns:
            The UserLemma junction object
        """
        user_lemma, created = cls.get_or_create(
            user_id=user_id,
            lemma=lemma,
        )

        # Set ignored_dt to current time if not already set
        if not user_lemma.ignored_dt:
            user_lemma.ignored_dt = datetime.now()
            user_lemma.save()

        return user_lemma

    @classmethod
    def unignore_lemma(cls, user_id: str, lemma: Lemma) -> bool:
        """Unignore a lemma for a user.

        Args:
            user_id: UUID of auth.users
            lemma: Lemma model

        Returns:
            True if the lemma was unignored, False if it wasn't ignored
        """
        try:
            user_lemma = cls.get(
                user_id=user_id,
                lemma=lemma,
                ignored_dt__is_null=False,
            )
            user_lemma.ignored_dt = None
            user_lemma.save()
            return True
        except DoesNotExist:
            return False


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
        Profile,
        UserLemma,
    ]  # Order matters for foreign key dependencies
