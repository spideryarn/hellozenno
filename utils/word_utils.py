from typing import TypedDict
from flask import abort
from peewee import DoesNotExist, prefetch
import unicodedata
from werkzeug.exceptions import NotFound

from db_models import Sourcedir, Sourcefile, SourcefileWordform, Wordform, Lemma
from utils.sourcedir_utils import _get_sourcefile_entry


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
            Wordform.wordform == word, Wordform.language_code == target_language_code
        )
    except DoesNotExist:
        # If not found, try case-insensitive match
        try:
            wordform = Wordform.get(
                fn.LOWER(Wordform.wordform) == word.lower(),
                Wordform.language_code == target_language_code,
            )
        except DoesNotExist:
            # If still not found, try normalized form (no diacritics)
            normalized_word = normalize_text(word)
            try:
                wordform = (
                    Wordform.select()
                    .where(Wordform.language_code == target_language_code)
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


def get_sourcedir_lemmas(language_code: str, sourcedir_slug: str) -> list[str]:
    """Get unique lemmas from all sourcefiles in a sourcedir."""
    try:
        sourcedir = (
            Sourcedir.select()
            .where(Sourcedir.slug == sourcedir_slug)
            .where(Sourcedir.language_code == language_code)
            .get()
        )
    except DoesNotExist:
        abort(404, description="Sourcedir not found")

    # Use the new optimized method to get lemmas for this sourcedir
    lemmas_query = Lemma.get_all_lemmas_for(
        language_code=language_code,
        sourcedir=sourcedir,
        sort_by="alpha"
    )
    lemmas = [row.lemma for row in lemmas_query]

    if not lemmas:
        abort(404, description="Directory contains no practice vocabulary")
    return lemmas


def get_sourcefile_lemmas(
    language_code: str, sourcedir_slug: str, sourcefile_slug: str
) -> list[str]:
    """
    Return a sorted, deduplicated list of lemma strings for all wordforms
    in the specified sourcefile. Raise NotFound if not found or if empty.
    """

    # Get the sourcefile using _get_sourcefile_entry
    sourcefile = _get_sourcefile_entry(language_code, sourcedir_slug, sourcefile_slug)

    # Use the new optimized method to get lemmas for this sourcefile
    query = Lemma.get_all_lemmas_for(
        language_code=language_code,
        sourcefile=sourcefile,
        sort_by="alpha"
    )

    # Collect lemma strings, ignoring any None
    lemmas = [row.lemma for row in query if row.lemma]
    if not lemmas:
        raise NotFound("Sourcefile contains no practice vocabulary.")

    return lemmas  # Already sorted by the query
