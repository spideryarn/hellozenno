"""
Utility functions for the flashcard system.
"""

from peewee import DoesNotExist

from db_models import Sourcedir, Sourcefile, SourcefileWordform, Sentence
from utils.lang_utils import get_language_name
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas
from utils.audio_utils import ensure_model_audio_data, get_or_create_sentence_audio
from utils.sentence_utils import get_random_sentence
from flask import url_for

# Import the exception
from utils.exceptions import AuthenticationRequiredForGenerationError


def get_flashcard_landing_data(
    target_language_code: str, sourcefile_slug=None, sourcedir_slug=None
):
    """
    Get data needed for the flashcard landing page.
    Used by both the view and API functions.

    Args:
        target_language_code: The target language code
        sourcefile_slug: Optional sourcefile slug to filter by
        sourcedir_slug: Optional sourcedir slug to filter by

    Returns:
        Dictionary with flashcard landing data, or None if an error occurred
    """
    language_name = get_language_name(target_language_code)

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None
    error = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
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
                target_language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
            lemma_count = len(lemmas) if lemmas else 0
        except DoesNotExist:
            error = "Sourcefile not found"

    if error:
        return {"error": error}

    return {
        "target_language_code": target_language_code,
        "language_name": language_name,
        "sourcefile": (
            {
                "slug": sourcefile_entry.slug,
                "name": sourcefile_entry.filename,
                "sourcedir_slug": sourcefile_entry.sourcedir.slug,
            }
            if sourcefile_entry
            else None
        ),
        "sourcedir": (
            {"slug": sourcedir_entry.slug, "name": sourcedir_entry.path}
            if sourcedir_entry
            else None
        ),
        "lemma_count": lemma_count,
    }


def get_flashcard_sentence_data(
    target_language_code: str, slug: str, sourcefile_slug=None, sourcedir_slug=None
):
    """
    Get data for a specific sentence flashcard.
    Used by both the view and API functions.

    Args:
        target_language_code: The target language code
        slug: The sentence slug
        sourcefile_slug: Optional sourcefile slug to filter by
        sourcedir_slug: Optional sourcedir slug to filter by

    Returns:
        Dictionary with sentence data or error information
    """
    language_name = get_language_name(target_language_code)

    try:
        sentence = Sentence.get(
            (Sentence.target_language_code == target_language_code)
            & (Sentence.slug == slug)
        )
    except DoesNotExist:
        return {"error": "Sentence not found"}

    # Default audio status flag
    audio_requires_login = False

    # Attempt to get or generate audio using the new utility
    try:
        audio_data, audio_requires_login = get_or_create_sentence_audio(
            sentence_model=sentence, should_add_delays=True, verbose=1
        )
    except Exception as e:
        # Log audio generation errors but continue, as audio can be generated on demand
        print(f"Error getting/generating audio for Sentence {sentence.id}: {e}")
        # If an unexpected error occurred (not AuthenticationRequired),
        # audio_requires_login remains False, but audio_data will be None
        # The frontend should handle the case where audio_url is present but audio fails to load.
        audio_data = None  # Ensure audio_data is None if there was an error

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            return {"error": "Sourcedir not found"}
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
                target_language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
            lemma_count = len(lemmas)
        except DoesNotExist:
            return {"error": "Sourcefile not found"}

    # Build response data
    response_data = {
        "id": sentence.id,
        "slug": sentence.slug,
        "text": sentence.sentence,
        "translation": sentence.translation,
        "lemma_words": sentence.lemma_words,
        "audio_url": (
            url_for(
                "sentence_api.get_sentence_audio_api",
                target_language_code=target_language_code,
                sentence_id=sentence.id,
            )
            if audio_data
            else None
        ),  # Only provide URL if audio data exists or could be generated
        "audio_requires_login": audio_requires_login,
        "metadata": {
            "target_language_code": target_language_code,
            "language_name": language_name,
        },
        "sentence": sentence,  # Include the full sentence model for views
    }

    # Add source information
    if sourcefile_entry:
        response_data["sourcefile"] = {
            "slug": sourcefile_entry.slug,
            "name": sourcefile_entry.filename,
            "sourcedir_slug": sourcefile_entry.sourcedir.slug,
        }
        response_data["metadata"]["sourcefile"] = sourcefile_entry.slug
    if sourcedir_entry:
        response_data["sourcedir"] = {
            "slug": sourcedir_entry.slug,
            "name": sourcedir_entry.path,
        }
        response_data["metadata"]["sourcedir"] = sourcedir_entry.slug

    response_data["lemma_count"] = lemma_count

    return response_data


def get_random_flashcard_data(
    target_language_code: str, sourcefile_slug=None, sourcedir_slug=None
):
    """
    Get data for a random sentence flashcard.
    Used by both the view and API functions.

    Args:
        target_language_code: The target language code
        sourcefile_slug: Optional sourcefile slug to filter by
        sourcedir_slug: Optional sourcedir slug to filter by

    Returns:
        Dictionary with random sentence data or error information

    Raises:
        AttributeError: If there's a database field mismatch
        Exception: For other unexpected errors
    """
    lemmas = None

    # If sourcedir is provided, get lemmas for filtering
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
        except DoesNotExist:
            return {"error": "Sourcedir not found", "status_code": 404}
    # If sourcefile is provided, get its lemmas for filtering
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(
                target_language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
        except DoesNotExist:
            return {"error": "Sourcefile not found", "status_code": 404}

    # Get random sentence
    sentence_data = get_random_sentence(
        target_language_code=target_language_code,
        required_lemmas=lemmas if lemmas else None,
    )

    if not sentence_data:
        # Return 204 (No Content) to distinguish between "no data" and actual errors
        return {"error": "No matching sentences found", "status_code": 204}

    return sentence_data
