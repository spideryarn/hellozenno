from typing import Any, Optional
from lang_utils import get_language_name
from vocab_llm_utils import metadata_for_lemma_full
from db_models import Lemma, Wordform, Phrase, DoesNotExist
from peewee import DatabaseError


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
        lemma, created = Lemma.update_or_create(
            lookup={"lemma": lemma, "language_code": target_language_code},
            updates=metadata,
        )
        return lemma  # type: ignore
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
    """
    metadata, _ = metadata_for_lemma_full(
        lemma=lemma, target_language_name=get_language_name(target_language_code)
    )
    metadata["is_complete"] = True
    lemma_model = save_lemma_metadata(lemma, metadata, target_language_code)
    return lemma_model.to_dict()


def load_or_generate_lemma_metadata(
    lemma: str, target_language_code: str, *, generate_if_incomplete: bool = False
):
    """Load metadata for a word lemma from database.

    Args:
        lemma: The lemma to load
        target_language_code: ISO language code (e.g. 'el' for Greek)
        check_complete: If True, verify metadata completeness and regenerate if incomplete

    Returns:
        Dictionary containing lemma metadata

    Raises:
        peewee.DatabaseError: If there's an error accessing the database
    """
    try:
        lemma_model = Lemma.get(
            Lemma.lemma == lemma, Lemma.language_code == target_language_code
        )
        metadata = lemma_model.to_dict()

        if generate_if_incomplete and not Lemma.check_metadata_completeness(metadata):
            return _generate_and_save_metadata(lemma, target_language_code)

        return metadata
    except DoesNotExist:
        print(f"No metadata found for lemma {lemma}, generating new metadata")
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
    query = Lemma.get_all_for_language(target_language_code, "alpha")
    lemmas = [lemma.lemma for lemma in query]

    # Helper function to get all wordforms for a lemma
    def get_all_wordforms(lemma: str) -> set[str]:
        try:
            lemma_model = Lemma.get(
                Lemma.lemma == lemma, Lemma.language_code == target_language_code
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
        wordform=wordform, language_code=target_language_code, metadata=metadata
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
