from typing import TypedDict
from flask import abort
from peewee import DoesNotExist, prefetch
import unicodedata

from db_models import Sourcedir, Sourcefile, SourcefileWordform, Wordform, Lemma


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


def get_word_preview(target_language_code: str, word: str) -> WordPreview | None:
    """Get preview data for a word tooltip."""
    from db_models import Wordform, fn

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

    lemmas_query = (
        Lemma.select(Lemma.lemma)
        .distinct()
        .join(Wordform)  # join via Wordform.lemma_entry foreign key
        .join(SourcefileWordform)  # join via SourcefileWordform.wordform foreign key
        .join(Sourcefile)  # join via SourcefileWordform.sourcefile foreign key
        .where(Sourcefile.sourcedir == sourcedir)
        .order_by(Lemma.lemma)
    )
    lemmas = [row.lemma for row in lemmas_query]

    if not lemmas:
        abort(404, description="Directory contains no practice vocabulary")
    return lemmas


def get_sourcefile_lemmas(
    language_code: str, sourcefile_slug: str, db=None
) -> list[str]:
    """Get unique lemmas from a sourcefile."""
    try:
        condition = (Sourcefile.slug == sourcefile_slug) & (
            Sourcefile.sourcedir.in_(
                Sourcedir.select(Sourcedir.id).where(
                    Sourcedir.language_code == language_code
                )
            )
        )
        if db:
            with db.bind_ctx([Sourcefile, Sourcedir]):
                sourcefile_entry = Sourcefile.select().where(condition).get()
        else:
            sourcefile_entry = Sourcefile.select().where(condition).get()
    except DoesNotExist:
        abort(404, description="Sourcefile not found")

    def run_query():
        query = (
            Lemma.select(Lemma.lemma)
            .distinct()
            .join(Wordform)  # join via Wordform.lemma_entry
            .join(SourcefileWordform)  # join via SourcefileWordform.wordform
            .where(SourcefileWordform.sourcefile == sourcefile_entry)
            .order_by(Lemma.lemma)
        )
        return [row.lemma for row in query]

    if db:
        with db.bind_ctx([Lemma, Wordform, SourcefileWordform, Sourcefile]):
            lemmas = run_query()
    else:
        lemmas = run_query()

    if not lemmas:
        abort(404, description="File contains no practice vocabulary")
    return lemmas
