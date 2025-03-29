"""
Utility functions for the flashcard system.
"""

from peewee import DoesNotExist

from db_models import Sourcedir, Sourcefile, SourcefileWordform
from utils.lang_utils import get_language_name
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas


def get_flashcard_landing_data(
    language_code: str, sourcefile_slug=None, sourcedir_slug=None
):
    """
    Get data needed for the flashcard landing page.
    Used by both the view and API functions.

    Args:
        language_code: The target language code
        sourcefile_slug: Optional sourcefile slug to filter by
        sourcedir_slug: Optional sourcedir slug to filter by

    Returns:
        Dictionary with flashcard landing data, or None if an error occurred
    """
    language_name = get_language_name(language_code)

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None
    error = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(language_code, sourcedir_slug)
            lemma_count = len(lemmas) if lemmas else 0
        except DoesNotExist:
            error = "Sourcedir not found"
    # If sourcefile is provided, get its lemma count
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(
                language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
            lemma_count = len(lemmas) if lemmas else 0
        except DoesNotExist:
            error = "Sourcefile not found"

    if error:
        return {"error": error}

    return {
        "language_code": language_code,
        "language_name": language_name,
        "sourcefile": (
            {
                "slug": sourcefile_entry.slug,
                "name": sourcefile_entry.name,
                "sourcedir_slug": sourcefile_entry.sourcedir.slug,
            }
            if sourcefile_entry
            else None
        ),
        "sourcedir": (
            {"slug": sourcedir_entry.slug, "name": sourcedir_entry.name}
            if sourcedir_entry
            else None
        ),
        "lemma_count": lemma_count,
    }
