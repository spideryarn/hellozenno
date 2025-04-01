"""Utility functions for phrases.

Contains shared functionality for phrase-related operations.
"""

from typing import Optional, List
from peewee import fn, DoesNotExist
from db_models import Phrase, RelatedPhrase, PhraseExampleSentence, Sentence


def get_phrases_query(target_language_code: str, sort_by: str = "alpha"):
    """Get query for phrases in specified language with sorting applied.

    Args:
        target_language_code: The language code to filter phrases by
        sort_by: Sort method - 'alpha' (alphabetical) or 'date' (by modification time)

    Returns:
        A Peewee SelectQuery with the specified filters and sorting applied
    """
    # Query phrases from database
    query = Phrase.select().where(Phrase.language_code == target_language_code)

    if sort_by == "date":
        # Sort by modification time, newest first
        query = query.order_by(fn.COALESCE(Phrase.updated_at, Phrase.created_at).desc())
    else:
        # Default alphabetical sort
        query = query.order_by(Phrase.canonical_form)

    return query


def get_phrase_by_slug(target_language_code: str, slug: str) -> Phrase:
    """Get a specific phrase by its language code and slug.

    Args:
        target_language_code: The language code to filter by
        slug: The slug of the phrase to retrieve

    Returns:
        The Phrase object if found with related data preloaded.
        The phrase object will have the following additional attributes:
        - related_to: List of RelatedPhrase objects where this phrase is the from_phrase
        - related_from: List of RelatedPhrase objects where this phrase is the to_phrase
        - example_sentences: List of PhraseExampleSentence objects for this phrase

    Raises:
        DoesNotExist: If no phrase with the given slug exists for the language
    """
    from db_models import RelatedPhrase, PhraseExampleSentence, Sentence

    # Find the phrase with eager loading of related data
    phrase = Phrase.get(
        (Phrase.language_code == target_language_code) & (Phrase.slug == slug)
    )

    # Prefetch related phrases (both directions)
    phrase.related_to = RelatedPhrase.select().where(
        RelatedPhrase.from_phrase == phrase.id
    )
    phrase.related_from = RelatedPhrase.select().where(
        RelatedPhrase.to_phrase == phrase.id
    )

    # Prefetch example sentences
    phrase.example_sentences = (
        PhraseExampleSentence.select(PhraseExampleSentence, Sentence)
        .join(Sentence)
        .where(PhraseExampleSentence.phrase == phrase.id)
    )

    return phrase
