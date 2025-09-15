from typing import Any, Optional
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import metadata_for_lemma_full
from db_models import Lemma, Wordform, Phrase, DoesNotExist
from peewee import DatabaseError

# Import the new exception and g for global context
from flask import g
from .exceptions import AuthenticationRequiredForGenerationError


def save_lemma_metadata(
    lemma: str, metadata: dict[str, Any], target_language_code: str
) -> Lemma:
    """Save metadata for a word lemma to database.

    Args:
        lemma: The lemma to save
        metadata: Dictionary containing lemma metadata
        target_language_code: ISO language code (e.g. 'el' for Greek)

    Raises:
        peewee.DatabaseError: If there's an error saving to the database
    """
    try:
        # Filter out lookup keys from updates to avoid duplicate kwargs on create
        updates_filtered = {
            k: v
            for k, v in metadata.items()
            if k not in {"lemma", "target_language_code"}
        }

        # Explicitly get the instance after update_or_create
        Lemma.update_or_create(
            lookup={
                "lemma": lemma,
                "target_language_code": target_language_code,
            },
            updates=updates_filtered,
        )
        # Fetch the instance to ensure correct type for return
        lemma_instance: Lemma = Lemma.get(
            Lemma.lemma == lemma,
            Lemma.target_language_code == target_language_code,
        )
        return lemma_instance
    except Exception as e:
        raise DatabaseError(f"Error saving lemma metadata: {e}") from e


def _generate_and_save_metadata(
    lemma: str, target_language_code: str
) -> dict[str, Any]:
    """Generate and save new metadata for a lemma.

    Args:
        lemma: The lemma to generate metadata for
        target_language_code: ISO language code

    Returns:
        The generated metadata dictionary

    Raises:
        AuthenticationRequiredForGenerationError: If user is not logged in.
    """
    # Check if user is logged in before allowing generation
    if not hasattr(g, "user") or g.user is None:
        raise AuthenticationRequiredForGenerationError(
            "User must be logged in to generate lemma metadata."
        )

    target_language_name = get_language_name(target_language_code)

    # Generate metadata using the LLM
    metadata, _ = metadata_for_lemma_full(
        lemma=lemma, target_language_name=target_language_name
    )

    # All lemmas should be marked as complete by default
    metadata["is_complete"] = True

    # Save to database
    lemma_model = save_lemma_metadata(lemma, metadata, target_language_code)
    return lemma_model.to_dict()


def load_or_generate_lemma_metadata(
    lemma: Optional[str],
    target_language_code: str,
    *,
    generate_if_incomplete: bool = False,
) -> dict[str, Any]:
    """Load metadata for a word lemma from database.

    Args:
        lemma: The lemma to load, or None if no lemma exists
        target_language_code: ISO language code (e.g. 'el' for Greek)
        generate_if_incomplete: If True, verify metadata completeness and regenerate if incomplete

    Returns:
        Dictionary containing lemma metadata

    Raises:
        peewee.DatabaseError: If there's an error accessing the database
        DoesNotExist: If lemma does not exist and generation fails
    """
    # Handle null or empty lemma
    if not lemma:
        return {
            "lemma": None,
            "translations": [],
            "etymology": "",
            "commonality": 0.5,
            "guessability": 0.5,
            "register": "unknown",
            "example_usage": [],
            "mnemonics": [],
            "related_words_phrases_idioms": [],
            "synonyms": [],
            "antonyms": [],
            "example_wordforms": [],
            "cultural_context": "",
            "is_complete": True,
            "notes": "No lemma available for this wordform",
        }

    try:
        # Try to find lemma in database
        lemma_model = Lemma.get(
            Lemma.lemma == lemma,
            Lemma.target_language_code == target_language_code,
        )
        metadata = lemma_model.to_dict()

        # Regenerate if incomplete and requested
        if generate_if_incomplete and not Lemma.check_metadata_completeness(metadata):
            return _generate_and_save_metadata(lemma, target_language_code)

        return metadata
    except DoesNotExist:
        # Lemma not found, generate new metadata
        return _generate_and_save_metadata(lemma, target_language_code)


def get_lemma_for_wordform(wordform: str, target_language_code: str) -> Optional[str]:
    """Find the lemma for a given word form."""
    # First try direct lookup in wordforms table
    wordform_model = Wordform.find_by_text(wordform, target_language_code)
    if wordform_model and wordform_model.lemma_entry:
        return wordform_model.lemma_entry.lemma

    # If not found, try searching through all lemmas' wordforms
    wordform_lower = wordform.lower()

    # Get all known lemmas for the language
    query = Lemma.get_all_lemmas_for(
        target_language_code=target_language_code, sort_by="alpha"
    )  # get_all_lemmas_for still uses target_language_code parameter
    lemmas = [lemma.lemma for lemma in query]

    # Helper function to get all wordforms for a lemma
    def get_all_wordforms(lemma: str) -> set[str]:
        try:
            lemma_model = Lemma.get(
                Lemma.lemma == lemma,
                Lemma.target_language_code == target_language_code,
            )
            return lemma_model.get_all_wordforms()
        except DoesNotExist:
            return {lemma}  # Return just the lemma if not found

    # Search through all lemmas' wordforms
    for lemma in lemmas:
        if wordform_lower in {w.lower() for w in get_all_wordforms(lemma)}:
            return lemma
    return None


def save_wordform_metadata(
    wordform: str, metadata: dict[str, Any], target_language_code: str
) -> None:
    """Save metadata for a wordform to database."""
    Wordform.get_or_create_from_metadata(
        wordform=wordform,
        target_language_code=target_language_code,
        metadata=metadata,
    )


def load_wordform_metadata(wordform: str, target_language_code: str) -> dict[str, Any]:
    """Load metadata for a wordform from database."""
    try:
        wordform_model = Wordform.find_by_text(wordform, target_language_code)
        if not wordform_model:
            raise DoesNotExist
        return wordform_model.to_dict()
    except DoesNotExist:
        raise FileNotFoundError(f"No metadata found for wordform: {wordform}")
