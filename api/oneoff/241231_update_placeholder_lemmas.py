"""Migration script to update placeholder lemmas with full metadata."""

import argparse
import sys
from pathlib import Path
from typing import Optional, Any, cast, Dict, List

from peewee import fn, TextField, CharField, FloatField
from playhouse.sqlite_ext import JSONField

# Add parent directory to path to import from project
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import init_db, database
from api.db_models import Lemma
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import metadata_for_lemma_full


def is_empty_or_default(value: Any) -> bool:
    """Check if a value is empty or has a default value."""
    if value is None:
        return True
    if isinstance(value, list) and not value:
        return True
    if isinstance(value, str) and value in ("", "unknown"):
        return True
    return False


def is_placeholder_lemma(lemma: Lemma) -> bool:
    """Check if a lemma is a placeholder with minimal data.

    A lemma is considered a placeholder if it has most of its fields empty
    or set to default values. We use a scoring system where each empty/default
    field adds to the score, and if the score is above a threshold, we consider
    it a placeholder.
    """
    score = 0
    total_fields = 0

    # Check each field
    if is_empty_or_default(lemma.part_of_speech):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.translations):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.etymology):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.synonyms):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.antonyms):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.related_words_phrases_idioms):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.register):
        score += 1
    total_fields += 1

    if lemma.commonality is None:
        score += 1
    total_fields += 1

    if lemma.guessability is None:
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.cultural_context):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.mnemonics):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.easily_confused_with):
        score += 1
    total_fields += 1

    if is_empty_or_default(lemma.example_usage):
        score += 1
    total_fields += 1

    # Consider it a placeholder if more than 75% of fields are empty/default
    threshold = 0.75
    return (score / total_fields) > threshold


def update_lemma_with_metadata(
    lemma: Lemma, dry_run: bool = False, verbose: bool = False
) -> Optional[Lemma]:
    """Update a lemma with full metadata from the LLM."""
    target_language_name = get_language_name(lemma.language_code)

    print(f"Updating lemma: {lemma.lemma} ({target_language_name})")
    if verbose:
        print("\nBefore update:")
        print(f"  part_of_speech: {lemma.part_of_speech}")
        print(f"  translations: {lemma.translations}")
        print(f"  etymology: {lemma.etymology}")
        print(f"  synonyms: {lemma.synonyms}")
        print(f"  antonyms: {lemma.antonyms}")
        print(f"  related_words_phrases_idioms: {lemma.related_words_phrases_idioms}")
        print(f"  register: {lemma.register}")
        print(f"  commonality: {lemma.commonality}")
        print(f"  guessability: {lemma.guessability}")
        print(f"  cultural_context: {lemma.cultural_context}")
        print(f"  mnemonics: {lemma.mnemonics}")
        print(f"  easily_confused_with: {lemma.easily_confused_with}")
        print(f"  example_usage: {lemma.example_usage}")

    # Get full metadata from LLM
    metadata, _ = metadata_for_lemma_full(
        lemma=str(lemma.lemma),  # Convert CharField to str
        target_language_name=target_language_name,
        verbose=1 if verbose else 0,
    )

    if verbose:
        print("\nGenerated metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    if not dry_run and isinstance(metadata, dict):
        # Update the lemma with new metadata
        lemma.part_of_speech = metadata.get("part_of_speech", "unknown")
        lemma.translations = metadata.get("translations", [])

        # Handle nullable fields with proper types
        if "etymology" in metadata:
            lemma.etymology = metadata["etymology"]
        if "synonyms" in metadata:
            lemma.synonyms = metadata["synonyms"]
        if "antonyms" in metadata:
            lemma.antonyms = metadata["antonyms"]
        if "related_words_phrases_idioms" in metadata:
            lemma.related_words_phrases_idioms = metadata[
                "related_words_phrases_idioms"
            ]
        if "register" in metadata:
            lemma.register = metadata["register"]
        if "commonality" in metadata:
            lemma.commonality = metadata["commonality"]
        if "guessability" in metadata:
            lemma.guessability = metadata["guessability"]
        if "cultural_context" in metadata:
            lemma.cultural_context = metadata["cultural_context"]
        if "mnemonics" in metadata:
            lemma.mnemonics = metadata["mnemonics"]
        if "easily_confused_with" in metadata:
            lemma.easily_confused_with = metadata["easily_confused_with"]
        if "example_usage" in metadata:
            lemma.example_usage = metadata["example_usage"]

        lemma.save()

        if verbose:
            print("\nAfter update:")
            print(f"  part_of_speech: {lemma.part_of_speech}")
            print(f"  translations: {lemma.translations}")
            print(f"  etymology: {lemma.etymology}")
            print(f"  synonyms: {lemma.synonyms}")
            print(f"  antonyms: {lemma.antonyms}")
            print(
                f"  related_words_phrases_idioms: {lemma.related_words_phrases_idioms}"
            )
            print(f"  register: {lemma.register}")
            print(f"  commonality: {lemma.commonality}")
            print(f"  guessability: {lemma.guessability}")
            print(f"  cultural_context: {lemma.cultural_context}")
            print(f"  mnemonics: {lemma.mnemonics}")
            print(f"  easily_confused_with: {lemma.easily_confused_with}")
            print(f"  example_usage: {lemma.example_usage}")

        return lemma

    return None


def main(
    dry_run: bool = False,
    language_code: Optional[str] = None,
    lemma_text: Optional[str] = None,
    verbose: bool = False,
):
    """Main migration function."""
    # Initialize database
    init_db()

    with database.atomic():
        # Get lemmas based on arguments
        if language_code and lemma_text:
            try:
                lemmas = [
                    Lemma.get(
                        Lemma.language_code == language_code, Lemma.lemma == lemma_text
                    )
                ]
                print(f"Found lemma: {lemma_text} ({language_code})")
            except Lemma.DoesNotExist:
                print(f"Lemma not found: {lemma_text} ({language_code})")
                return
        else:
            # Get all lemmas
            lemmas = Lemma.select()

        # Find placeholder lemmas
        placeholder_lemmas = [lemma for lemma in lemmas if is_placeholder_lemma(lemma)]

        print(
            f"Found {len(placeholder_lemmas)} placeholder lemmas out of {len(lemmas)} total"
        )

        if dry_run:
            print("\nDRY RUN - No changes will be made")
            for lemma in placeholder_lemmas:
                empty_fields = []
                if is_empty_or_default(lemma.part_of_speech):
                    empty_fields.append("part_of_speech")
                if is_empty_or_default(lemma.translations):
                    empty_fields.append("translations")
                if is_empty_or_default(lemma.etymology):
                    empty_fields.append("etymology")
                if is_empty_or_default(lemma.synonyms):
                    empty_fields.append("synonyms")
                if is_empty_or_default(lemma.antonyms):
                    empty_fields.append("antonyms")
                if is_empty_or_default(lemma.related_words_phrases_idioms):
                    empty_fields.append("related_words_phrases_idioms")
                if is_empty_or_default(lemma.register):
                    empty_fields.append("register")
                if lemma.commonality is None:
                    empty_fields.append("commonality")
                if lemma.guessability is None:
                    empty_fields.append("guessability")
                if is_empty_or_default(lemma.cultural_context):
                    empty_fields.append("cultural_context")
                if is_empty_or_default(lemma.mnemonics):
                    empty_fields.append("mnemonics")
                if is_empty_or_default(lemma.easily_confused_with):
                    empty_fields.append("easily_confused_with")
                if is_empty_or_default(lemma.example_usage):
                    empty_fields.append("example_usage")
                print(f"Would update: {lemma.lemma} ({lemma.language_code})")
                print(f"  Empty/default fields: {', '.join(empty_fields)}")
            return

        # Update each placeholder lemma
        for lemma in placeholder_lemmas:
            try:
                updated_lemma = update_lemma_with_metadata(
                    lemma, dry_run=dry_run, verbose=verbose
                )
                if updated_lemma:
                    print(f"Successfully updated {lemma.lemma}")
            except Exception as e:
                print(f"Error updating {lemma.lemma}: {e}")
                database.rollback()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update placeholder lemmas with full metadata"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes to see what would be updated",
    )
    parser.add_argument(
        "--language-code",
        help="Optional language code to update a specific lemma",
    )
    parser.add_argument(
        "--lemma",
        help="Optional lemma text to update (requires --language-code)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    args = parser.parse_args()

    if args.lemma and not args.language_code:
        parser.error("--lemma requires --language-code")

    if args.dry_run:
        print("Running in dry-run mode - no changes will be made")
    main(
        dry_run=args.dry_run,
        language_code=args.language_code,
        lemma_text=args.lemma,
        verbose=args.verbose,
    )
