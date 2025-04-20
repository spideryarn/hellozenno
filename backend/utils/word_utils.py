from typing import TypedDict
from flask import abort, g
from peewee import DoesNotExist, prefetch
import unicodedata
from werkzeug.exceptions import NotFound

from db_models import Sourcedir, Sourcefile, SourcefileWordform, Wordform, Lemma
from utils.lang_utils import get_language_name
from utils.sourcefile_utils import _get_sourcefile_entry
from .exceptions import AuthenticationRequiredForGenerationError


class WordPreview(TypedDict):
    lemma: str
    translation: str
    etymology: str | None


def normalize_text(text: str) -> str:
    """Normalize text by converting to lowercase and removing diacritics."""
    # Convert to lowercase first
    text = text.lower()
    # Normalize to NFKD to separate base characters from combining marks
    text = unicodedata.normalize("NFKD", text)
    # Remove combining diacritical marks
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Normalize back to NFKC for good measure
    text = unicodedata.normalize("NFKC", text)
    return text


def ensure_nfc(text: str) -> str:
    """Ensure text is in NFC (Normalization Form C) for consistent handling.

    This standardizes all Unicode text to use the composed form where characters
    with diacritics are represented as single code points rather than base characters
    plus combining marks.
    """
    return unicodedata.normalize("NFC", text)


def get_word_preview(target_language_code: str, word: str) -> WordPreview | None:
    """Get preview data for a word tooltip."""
    from db_models import Wordform, fn

    # Ensure consistent NFC normalization for lookups
    word = ensure_nfc(word)

    try:
        # First try exact match
        wordform = Wordform.get(
            Wordform.wordform == word,
            Wordform.target_language_code == target_language_code,
        )
    except DoesNotExist:
        # If not found, try case-insensitive match
        try:
            wordform = Wordform.get(
                fn.LOWER(Wordform.wordform) == word.lower(),
                Wordform.target_language_code == target_language_code,
            )
        except DoesNotExist:
            # If still not found, try normalized form (no diacritics)
            normalized_word = normalize_text(word)
            try:
                wordform = (
                    Wordform.select()
                    .where(Wordform.target_language_code == target_language_code)
                    .where(fn.LOWER(Wordform.wordform) == normalized_word)
                    .get()
                )
            except DoesNotExist:
                return None

    lemma_entry = wordform.lemma_entry
    return {
        "lemma": lemma_entry.lemma if lemma_entry else word,
        "translation": (
            "; ".join(wordform.translations) if wordform.translations else ""
        ),
        "etymology": lemma_entry.etymology if lemma_entry else None,
    }


def get_sourcedir_lemmas(target_language_code: str, sourcedir_slug: str) -> list[str]:
    """Get unique lemmas from all sourcefiles in a sourcedir."""
    try:
        sourcedir = (
            Sourcedir.select()
            .where(Sourcedir.slug == sourcedir_slug)
            .where(Sourcedir.target_language_code == target_language_code)
            .get()
        )
    except DoesNotExist:
        abort(404, description="Sourcedir not found")

    # Use a simple, direct query that will always work even in test environments
    # This query doesn't use any problematic SQL features (like ORDER BY on expressions not in SELECT)
    simple_query = (
        Lemma.select(Lemma.lemma)
        .distinct()
        .join(Wordform, on=Wordform.lemma_entry)
        .join(SourcefileWordform, on=SourcefileWordform.wordform)
        .join(Sourcefile, on=SourcefileWordform.sourcefile)
        .where(
            (Lemma.target_language_code == target_language_code)
            & (Sourcefile.sourcedir == sourcedir)
        )
        .order_by(Lemma.lemma)  # Simple ordering by column, not expression
    )

    # Execute the query and get the results
    results = list(simple_query)
    lemmas = [row.lemma for row in results if row.lemma]

    # If no lemmas found, abort with 404
    if not lemmas:
        abort(404, description="Directory contains no practice vocabulary")

    return lemmas


def get_sourcefile_lemmas(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
) -> list[str]:
    """
    Return a sorted, deduplicated list of lemma strings for all wordforms
    in the specified sourcefile. Raise NotFound if not found or if empty.
    """

    # Get the sourcefile using _get_sourcefile_entry
    sourcefile = _get_sourcefile_entry(
        target_language_code, sourcedir_slug, sourcefile_slug
    )

    # Use a simple, direct query that will always work even in test environments
    # This query doesn't use any problematic SQL features (like ORDER BY on expressions not in SELECT)
    # but is still efficient for this operation
    simple_query = (
        Lemma.select(Lemma.lemma)
        .distinct()
        .join(Wordform, on=Wordform.lemma_entry)
        .join(SourcefileWordform, on=SourcefileWordform.wordform)
        .where(
            (Lemma.target_language_code == target_language_code)
            & (SourcefileWordform.sourcefile == sourcefile)
        )
        .order_by(Lemma.lemma)  # Simple ordering by column, not expression
    )

    # Execute the query and get the results
    results = list(simple_query)
    lemmas = [row.lemma for row in results if row.lemma]

    # If no lemmas found, raise NotFound
    if not lemmas:
        raise NotFound("Sourcefile contains no practice vocabulary.")

    return lemmas


def get_wordform_metadata(target_language_code: str, wordform: str):
    """
    Get metadata for a specific wordform.

    Args:
        target_language_code: The language code (e.g. 'el' for Greek)
        wordform: The wordform text

    Returns:
        A dictionary containing:
        - wordform_metadata: The wordform data
        - lemma_metadata: Associated lemma data if available
        - metadata: Creation/update timestamps

    Raises:
        DoesNotExist: If wordform not found
    """

    # Ensure wordform is properly handled
    wordform = ensure_nfc(wordform)

    # First try to find existing wordform in database
    wordform_model = Wordform.get(
        Wordform.wordform == wordform,
        Wordform.target_language_code == target_language_code,
    )

    # Get the data
    wordform_metadata = wordform_model.to_dict()

    # Split the inflection_type string into a list if it exists
    wordform_metadata["inflection_types"] = (
        wordform_metadata["inflection_type"].split()
        if wordform_metadata["inflection_type"]
        else []
    )

    lemma_metadata = (
        wordform_model.lemma_entry.to_dict() if wordform_model.lemma_entry else {}
    )

    # Prepare metadata timestamps
    metadata = {
        "created_at": wordform_model.created_at,
        "updated_at": wordform_model.updated_at,
    }

    result = {
        "wordform_metadata": wordform_metadata,
        "lemma_metadata": lemma_metadata,
        "target_language_code": target_language_code,
        "target_language_name": get_language_name(target_language_code),
        "metadata": metadata,
    }

    return result


def find_or_create_wordform(target_language_code: str, wordform: str):
    """
    Find or create a wordform, handling common search behavior.

    This shared utility function handles the common logic used by both
    get_wordform_metadata_vw and get_wordform_metadata_api.

    This function now synchronously waits for wordform generation to complete
    when a new wordform needs to be created.

    Args:
        target_language_code: The language code (e.g. 'el' for Greek)
        wordform: The wordform text

    Returns:
        A dictionary with the following structure:
        {
            "status": str, # "found", "multiple_matches", "redirect", or "invalid"
            "data": dict,  # The result data appropriate for the status
        }
    """
    from utils.vocab_llm_utils import quick_search_for_wordform
    from peewee import DoesNotExist
    from loguru import logger

    # Ensure wordform is properly handled
    wordform = ensure_nfc(wordform)

    try:
        # Try to find existing wordform in database
        result = get_wordform_metadata(target_language_code, wordform)
        return {"status": "found", "data": result}
    except DoesNotExist:
        # Wordform not found. Generation/AI search is needed.
        # Check if user is logged in.
        if not hasattr(g, "user") or g.user is None:
            logger.warning(f"Auth required for wordform generation: '{wordform}'")
            raise AuthenticationRequiredForGenerationError(
                "Authentication required to search for or generate wordform details."
            )

        # User is logged in, proceed with AI search/generation
        logger.info(f"Wordform '{wordform}' not found, generating with AI...")
        search_result, _ = quick_search_for_wordform(wordform, target_language_code, 1)

        # Count total matches from both result types
        target_matches = search_result["target_language_results"]["matches"]
        english_matches = search_result["english_results"]["matches"]
        total_matches = len(target_matches) + len(english_matches)

        # Check for possible misspellings
        target_misspellings = search_result["target_language_results"][
            "possible_misspellings"
        ]
        english_misspellings = search_result["english_results"]["possible_misspellings"]

        # If there are multiple matches or misspellings, return search results
        if total_matches > 1 or target_misspellings or english_misspellings:
            logger.info(f"Multiple matches or misspellings found for '{wordform}'")
            return {
                "status": "multiple_matches",
                "data": {
                    "target_language_code": target_language_code,
                    "target_language_name": get_language_name(target_language_code),
                    "search_term": wordform,
                    "target_language_results": search_result["target_language_results"],
                    "english_results": search_result["english_results"],
                },
            }

        # If there's exactly one match, create that wordform and return the data
        elif total_matches == 1:
            # Get the single match (either from target or english results)
            match = target_matches[0] if target_matches else english_matches[0]
            match_wordform = match.get("target_language_wordform")

            if match_wordform:
                logger.info(f"Creating wordform '{match_wordform}' in database")
                # Convert from new response format to metadata format
                metadata = {
                    "wordform": match_wordform,
                    "lemma": match.get("target_language_lemma"),
                    "part_of_speech": match.get("part_of_speech"),
                    "translations": match.get("english", []),
                    "inflection_type": match.get("inflection_type"),
                    "possible_misspellings": None,
                }

                # Create the wordform in the database
                Wordform.get_or_create_from_metadata(
                    wordform=match_wordform,
                    target_language_code=target_language_code,
                    metadata=metadata,
                )

                # Now that the wordform is created, fetch the complete metadata
                try:
                    # Directly return the complete data instead of redirecting
                    result = get_wordform_metadata(target_language_code, match_wordform)
                    logger.info(f"Wordform '{match_wordform}' created successfully")
                    return {"status": "found", "data": result}
                except Exception as e:
                    logger.error(f"Error after creating wordform: {e}")
                    # Fallback to redirect if there's an error getting the complete data
                    return {
                        "status": "redirect",
                        "data": {
                            "target_language_code": target_language_code,
                            "target_language_name": get_language_name(
                                target_language_code
                            ),
                            "redirect_to": match_wordform,
                        },
                    }

        # If no matches or misspellings, return invalid word data
        logger.info(f"No valid matches found for '{wordform}'")
        return {
            "status": "invalid",
            "data": {
                "error": "Not Found",
                "description": f"Wordform '{wordform}' not found",
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
                "wordform": wordform,
                "possible_misspellings": target_misspellings,
            },
        }
