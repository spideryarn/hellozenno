"""
Utility functions for the flashcard system.
"""

from peewee import DoesNotExist

from db_models import (
    Sourcedir,
    Sourcefile,
    SourcefileWordform,
    Sentence,
    SentenceAudio,
    Wordform,
)
from utils.lang_utils import get_language_name
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas, normalize_text
from utils.audio_utils import ensure_sentence_audio_variants
from utils.sentence_utils import get_random_sentence
from utils.vocab_llm_utils import extract_tokens, create_interactive_word_data
from flask import url_for

# Import the exception
from utils.exceptions import AuthenticationRequiredForGenerationError


def _make_error(
    *, error_code: str, message: str, status_code: int = 404, details: dict | None = None
) -> dict:
    """Create a structured error payload for flashcard endpoints.

    Includes an error_code, human message, HTTP-ish status_code hint, and optional details.
    """
    payload = {
        "error": message,
        "error_code": error_code,
        "status_code": status_code,
    }
    if details:
        payload["details"] = details
    return payload


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
            sourcedir_entry = Sourcedir.get(
                (Sourcedir.slug == sourcedir_slug)
                & (Sourcedir.target_language_code == target_language_code)
            )
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
            lemma_count = len(lemmas) if lemmas else 0
        except DoesNotExist:
            error = "Sourcedir not found"
    # If sourcefile is provided, get its lemma count
    elif sourcefile_slug:
        try:
            # Validate the sourcefile belongs to the target language via its sourcedir
            sourcefile_entry = (
                Sourcefile.select()
                .join(Sourcedir)
                .where(
                    (Sourcefile.slug == sourcefile_slug)
                    & (Sourcedir.target_language_code == target_language_code)
                )
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

    audio_requires_login = False
    variants = []

    try:
        variants, _ = ensure_sentence_audio_variants(sentence)
    except AuthenticationRequiredForGenerationError:
        audio_requires_login = True
        variants = list(sentence.audio_variants.order_by(SentenceAudio.created_at))  # type: ignore
    except Exception as e:
        print(f"Error getting/generating audio for Sentence {sentence.id}: {e}")
        variants = list(sentence.audio_variants.order_by(SentenceAudio.created_at))  # type: ignore

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(
                (Sourcedir.slug == sourcedir_slug)
                & (Sourcedir.target_language_code == target_language_code)
            )
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            return {"error": "Sourcedir not found"}
    # If sourcefile is provided, get its lemma count
    elif sourcefile_slug:
        try:
            # Validate the sourcefile belongs to the target language via its sourcedir
            sourcefile_entry = (
                Sourcefile.select()
                .join(Sourcedir)
                .where(
                    (Sourcefile.slug == sourcefile_slug)
                    & (Sourcedir.target_language_code == target_language_code)
                )
                .get()
            )
            lemmas = get_sourcefile_lemmas(
                target_language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
            lemma_count = len(lemmas)
        except DoesNotExist:
            return {"error": "Sourcefile not found"}

    # Add word recognition data for enhanced text tooltips
    recognized_words = []
    try:
        # Extract tokens from the sentence text
        tokens_in_text = extract_tokens(str(sentence.sentence))

        # Query database for all wordforms in this language that might be in the text
        wordforms = list(
            Wordform.select().where(
                (Wordform.target_language_code == target_language_code)
            )
        )

        # Filter wordforms in Python using normalize_text to match tokens
        normalized_tokens = {normalize_text(t) for t in tokens_in_text}
        matching_wordforms = [
            wf for wf in wordforms if normalize_text(wf.wordform) in normalized_tokens
        ]

        # Convert to dictionary format for create_interactive_word_data
        wordforms_d = []
        for wordform in matching_wordforms:
            wordform_d = wordform.to_dict()
            wordforms_d.append(wordform_d)

        # Create structured word recognition data
        recognized_words, found_wordforms = create_interactive_word_data(
            text=str(sentence.sentence),
            wordforms=wordforms_d,
            target_language_code=target_language_code,
        )
    except Exception as e:
        # Log error but don't fail the entire request
        print(f"Error generating word recognition data for sentence {sentence.id}: {e}")
        recognized_words = []

    # Build response data
    response_data = {
        "id": sentence.id,
        "slug": sentence.slug,
        "text": sentence.sentence,
        "translation": sentence.translation,
        "lemma_words": sentence.lemma_words,
        "recognized_words": recognized_words,  # Add word recognition data
        "audio_url": (
            url_for(
                "sentence_api.get_sentence_audio_api",
                target_language_code=target_language_code,
                sentence_id=sentence.id,
            )
            if variants
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
    target_language_code: str, sourcefile_slug=None, sourcedir_slug=None, profile=None
):
    """
    Get data for a random sentence flashcard.
    Used by both the view and API functions.

    Args:
        target_language_code: The target language code
        sourcefile_slug: Optional sourcefile slug to filter by
        sourcedir_slug: Optional sourcedir slug to filter by
        profile: Optional Profile model to filter out ignored lemmas

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
            sourcedir_entry = Sourcedir.get(
                (Sourcedir.slug == sourcedir_slug)
                & (Sourcedir.target_language_code == target_language_code)
            )
            lemmas = get_sourcedir_lemmas(target_language_code, sourcedir_slug)
            if not lemmas:
                return _make_error(
                    error_code="sourcedir_has_no_vocabulary",
                    message="Directory contains no processed vocabulary",
                    status_code=404,
                    details={
                        "target_language_code": target_language_code,
                        "sourcedir_slug": sourcedir_slug,
                        "lemma_count": 0,
                    },
                )
        except DoesNotExist:
            return _make_error(
                error_code="invalid_sourcedir_slug",
                message="Sourcedir not found",
                status_code=404,
                details={
                    "target_language_code": target_language_code,
                    "sourcedir_slug": sourcedir_slug,
                },
            )
    # If sourcefile is provided, get its lemmas for filtering
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(Sourcedir)
                .where(
                    (Sourcefile.slug == sourcefile_slug)
                    & (Sourcedir.target_language_code == target_language_code)
                )
                .get()
            )
            lemmas = get_sourcefile_lemmas(
                target_language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
            if not lemmas:
                return _make_error(
                    error_code="sourcefile_has_no_vocabulary",
                    message="Source file contains no processed vocabulary",
                    status_code=404,
                    details={
                        "target_language_code": target_language_code,
                        "sourcefile_slug": sourcefile_slug,
                        "sourcedir_slug": sourcefile_entry.sourcedir.slug,
                        "lemma_count": 0,
                    },
                )
        except DoesNotExist:
            return _make_error(
                error_code="invalid_sourcefile_slug",
                message="Sourcefile not found",
                status_code=404,
                details={
                    "target_language_code": target_language_code,
                    "sourcefile_slug": sourcefile_slug,
                },
            )

    # If there are no sentences at all for this language, surface that specifically
    total_sentences = (
        Sentence.select()
        .where(Sentence.target_language_code == target_language_code)
        .count()
    )
    if total_sentences == 0:
        return _make_error(
            error_code="no_sentences_for_language",
            message="No sentences available for this language",
            status_code=404,
            details={
                "target_language_code": target_language_code,
                "total_sentences": 0,
            },
        )

    # Get random sentence
    sentence_data = get_random_sentence(
        target_language_code=target_language_code,
        required_lemmas=lemmas if lemmas else None,
        profile=profile,
    )

    if not sentence_data:
        # Differentiate between no results with lemmas vs generic no results
        if lemmas:
            return _make_error(
                error_code="no_sentences_match_required_lemmas",
                message="No sentences contain the selected vocabulary",
                status_code=404,
                details={
                    "target_language_code": target_language_code,
                    "lemma_count": len(lemmas),
                    "sample_lemmas": list(lemmas)[:5] if isinstance(lemmas, list) else None,
                },
            )
        return _make_error(
            error_code="no_sentences_for_language",
            message="No sentences available for this language",
            status_code=404,
            details={
                "target_language_code": target_language_code,
                "total_sentences": 0,
            },
        )

    return sentence_data
