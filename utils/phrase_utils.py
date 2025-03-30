"""Utility functions for phrases.

Contains shared functionality for phrase-related operations.
"""

from typing import Optional, List
from peewee import fn, DoesNotExist
from db_models import Phrase


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
        The Phrase object if found

    Raises:
        DoesNotExist: If no phrase with the given slug exists for the language
    """
    return Phrase.get(
        (Phrase.language_code == target_language_code) & (Phrase.slug == slug)
    )
