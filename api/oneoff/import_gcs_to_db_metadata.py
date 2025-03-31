"""One-off scripts for data migration and maintenance."""

import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging
from datetime import datetime

from config import GOOGLE_CLOUD_STORAGE_BUCKET, SUPPORTED_LANGUAGES
from utils.db_connection import database, init_db
from db_models import (
    Wordform,
    Lemma,
    Sentence,
    Phrase,
    LemmaExampleSentence,
    PhraseExampleSentence,
    RelatedPhrase,
)
from obsolete.google_cloud_storage_utils import list_blobs, read_json
from paths import get_wordforms_dir
from utils.logging_utils import setup_logging
from utils.lang_utils import get_language_name


"""
GOOGLE_CLOUD_PROJECT=hello-zenno GOOGLE_CLOUD_STORAGE_BUCKET=hello-zenno-storage python oneoff.py
"""


def setup_database(dry_run: bool) -> None:
    """Initialize database and create tables."""
    init_db()
    logger = setup_logging()
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Database initialized")

    if not dry_run:
        with database:
            # Drop all tables in reverse order to handle foreign key dependencies
            database.drop_tables(
                [
                    RelatedPhrase,
                    PhraseExampleSentence,
                    LemmaExampleSentence,
                    Phrase,
                    Sentence,
                    Wordform,
                    Lemma,
                ],
                safe=True,
            )
            logger.info("Dropped existing tables")

            # Create tables in correct order
            database.create_tables(
                [
                    Lemma,
                    Wordform,
                    Sentence,
                    Phrase,
                    LemmaExampleSentence,
                    PhraseExampleSentence,
                    RelatedPhrase,
                ]
            )
            logger.info("Created tables")


def create_or_update_lemma(
    data: dict, language_code: str, dry_run: bool
) -> Optional[Lemma]:
    """Create a new lemma or update an existing one with new information."""
    logger = setup_logging()
    if not data.get("lemma"):
        return None

    lemma_data = {
        "lemma": data["lemma"],
        "language_code": language_code,
        "part_of_speech": data.get("part_of_speech"),
        "translations": data.get("translations", []),
        "etymology": data.get("etymology"),
        "synonyms": data.get("synonyms"),
        "antonyms": data.get("antonyms"),
        "related_words_phrases_idioms": data.get("related_words_phrases_idioms"),
        "register": data.get("register"),
        "commonality": data.get("commonality"),
        "guessability": data.get("guessability"),
        "cultural_context": data.get("cultural_context"),
        "mnemonics": data.get("mnemonics"),
        "easily_confused_with": data.get("easily_confused_with"),
    }

    if not dry_run:
        try:
            lemma_entry, created = Lemma.get_or_create(
                lemma=data["lemma"],
                language_code=language_code,
                defaults=lemma_data,
            )

            if not created:
                # Update existing entry with any new non-None values
                update_data = {k: v for k, v in lemma_data.items() if v is not None}
                if update_data:
                    for key, value in update_data.items():
                        setattr(lemma_entry, key, value)
                    lemma_entry.save()
                    logger.debug(f"Updated lemma: {data['lemma']}")
            else:
                logger.debug(f"Created new lemma: {data['lemma']}")

            return lemma_entry
        except Exception as e:
            logger.error(f"Error processing lemma {data['lemma']}: {str(e)}")
            return None
    return None


def create_or_get_sentence(
    data: dict, language_code: str, dry_run: bool
) -> Optional[Sentence]:
    """Create or get a sentence entry."""
    logger = setup_logging()
    if not data.get("sentence"):
        return None

    sentence_data = {
        "language_code": language_code,
        "sentence": data["sentence"],
        "translation": data.get("translation", ""),
        "lemma_words": data.get("lemma_words", []),
    }

    if not dry_run:
        try:
            sentence_entry, created = Sentence.get_or_create(
                sentence=data["sentence"],
                language_code=language_code,
                defaults=sentence_data,
            )
            logger.debug(
                f"{'Created' if created else 'Found'} sentence: {data['sentence'][:50]}..."
            )
            return sentence_entry
        except Exception as e:
            logger.error(f"Error processing sentence: {str(e)}")
            return None
    return None


def create_or_get_phrase(
    data: dict, language_code: str, dry_run: bool
) -> Optional[Phrase]:
    """Create or get a phrase entry."""
    logger = setup_logging()
    if not data.get("canonical_form"):
        return None

    phrase_data = {
        "language_code": language_code,
        "canonical_form": data["canonical_form"],
        "raw_forms": data.get("raw_forms", []),
        "translations": data.get("translations", []),
        "part_of_speech": data.get("part_of_speech", ""),
        "register": data.get("register"),
        "commonality": data.get("commonality"),
        "guessability": data.get("guessability"),
        "etymology": data.get("etymology"),
        "cultural_context": data.get("cultural_context"),
        "mnemonics": data.get("mnemonics"),
        "component_words": data.get("component_words"),
        "usage_notes": data.get("usage_notes"),
        "difficulty_level": data.get("difficulty_level"),
    }

    if not dry_run:
        try:
            phrase_entry, created = Phrase.get_or_create(
                canonical_form=data["canonical_form"],
                language_code=language_code,
                defaults=phrase_data,
            )
            logger.debug(
                f"{'Created' if created else 'Found'} phrase: {data['canonical_form']}"
            )
            return phrase_entry
        except Exception as e:
            logger.error(f"Error processing phrase: {str(e)}")
            return None
    return None


def prepare_wordform_data(
    data: dict, wordform: str, lemma_entry: Optional[Lemma], language_code: str
) -> dict:
    """Prepare wordform record data."""
    return {
        "wordform": wordform if data.get("wordform") is None else data["wordform"],
        "lemma_entry": lemma_entry,
        "language_code": language_code,
        "part_of_speech": data.get("part_of_speech"),
        "translations": data.get("translations"),
        "inflection_type": data.get("inflection_type"),
        "possible_misspellings": data.get("possible_misspellings"),
        "is_lemma": (data.get("lemma") == wordform if data.get("lemma") else False),
    }


def process_wordform_file(
    json_path: str, language_code: str, bucket_name: str, dry_run: bool
) -> Optional[Dict[str, Any]]:
    """Process a single wordform JSON file."""
    logger = setup_logging()
    try:
        data = read_json(bucket_name=bucket_name, source_blob=json_path)
        wordform = Path(json_path).stem

        # Handle lemma creation/retrieval
        lemma_entry = create_or_update_lemma(data, language_code, dry_run)

        # Prepare and create wordform
        record_data = prepare_wordform_data(data, wordform, lemma_entry, language_code)

        if not dry_run:
            # Use get_or_create to make it idempotent
            wordform_entry, created = Wordform.get_or_create(
                wordform=record_data["wordform"],
                language_code=language_code,
                defaults=record_data,
            )
            if created:
                logger.debug(f"Created new wordform: {record_data['wordform']}")
            else:
                logger.debug(f"Found existing wordform: {record_data['wordform']}")
        else:
            logger.debug(f"Would create wordform: {record_data}")

        return record_data

    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        return None


def process_sentence_file(
    json_path: str, language_code: str, bucket_name: str, dry_run: bool
) -> Optional[Dict[str, Any]]:
    """Process a single sentence JSON file."""
    logger = setup_logging()
    try:
        data = read_json(bucket_name=bucket_name, source_blob=json_path)
        sentence_entry = create_or_get_sentence(data, language_code, dry_run)

        # Process any associated lemmas
        if not dry_run and sentence_entry and data.get("lemma_words"):
            for lemma_word in data["lemma_words"]:
                lemma_entry = create_or_update_lemma(
                    {"lemma": lemma_word}, language_code, dry_run
                )
                if lemma_entry:
                    LemmaExampleSentence.get_or_create(
                        lemma=lemma_entry, sentence=sentence_entry
                    )

        return data
    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        return None


def process_phrase_file(
    json_path: str, language_code: str, bucket_name: str, dry_run: bool
) -> Optional[Dict[str, Any]]:
    """Process a single phrase JSON file."""
    logger = setup_logging()
    try:
        data = read_json(bucket_name=bucket_name, source_blob=json_path)
        phrase_entry = create_or_get_phrase(data, language_code, dry_run)

        if not dry_run and phrase_entry:
            # Process example sentences
            if data.get("example_sentences"):
                for sentence_data in data["example_sentences"]:
                    sentence_entry = create_or_get_sentence(
                        sentence_data, language_code, dry_run
                    )
                    if sentence_entry:
                        example, created = PhraseExampleSentence.get_or_create(
                            phrase=phrase_entry,
                            sentence=sentence_entry,
                            context=sentence_data.get("context"),
                        )
                        logger.debug(
                            f"{'Created' if created else 'Found'} example sentence for phrase {phrase_entry.canonical_form}"
                        )

            # Process related phrases
            if data.get("related_phrases"):
                for related_data in data["related_phrases"]:
                    if not related_data.get("canonical_form"):
                        continue

                    # Create the related phrase first
                    related_phrase = create_or_get_phrase(
                        {"canonical_form": related_data["canonical_form"]},
                        language_code,
                        dry_run,
                    )
                    if related_phrase:
                        relation, created = RelatedPhrase.get_or_create(
                            from_phrase=phrase_entry,
                            to_phrase=related_phrase,
                            relationship_type=related_data.get(
                                "relationship", "related"
                            ),
                        )
                        logger.debug(
                            f"{'Created' if created else 'Found'} relationship between {phrase_entry.canonical_form} and {related_phrase.canonical_form}"
                        )

        return data
    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        return None


def process_lemma_file(
    json_path: str, language_code: str, bucket_name: str, dry_run: bool
) -> Optional[Dict[str, Any]]:
    """Process a single lemma JSON file."""
    logger = setup_logging()
    try:
        data = read_json(bucket_name=bucket_name, source_blob=json_path)
        lemma_entry = create_or_update_lemma(data, language_code, dry_run)

        # Process any example sentences
        if not dry_run and lemma_entry and data.get("example_sentences"):
            for sentence_data in data["example_sentences"]:
                sentence_entry = create_or_get_sentence(
                    sentence_data, language_code, dry_run
                )
                if sentence_entry:
                    LemmaExampleSentence.get_or_create(
                        lemma=lemma_entry, sentence=sentence_entry
                    )

        return data
    except Exception as e:
        logger.error(f"Error processing {json_path}: {str(e)}")
        return None


def import_all_from_gcs(
    dry_run: bool = False, language_code: Optional[str] = None
) -> None:
    """
    Import all data types from Google Cloud Storage into the database.

    Args:
        dry_run: If True, don't actually write to database
        language_code: Optional 2-letter language code to process only one language
    """
    # Set up logging to both file and console
    logger = setup_logging()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"import_log_{timestamp}.txt"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    logger.info(f"Starting import. Log file: {log_file}")
    if language_code:
        logger.info(f"Processing only language: {language_code}")
    else:
        logger.info("Processing all supported languages")

    if not isinstance(GOOGLE_CLOUD_STORAGE_BUCKET, str):
        raise ValueError("GOOGLE_CLOUD_STORAGE_BUCKET must be a string")
    bucket_name = str(GOOGLE_CLOUD_STORAGE_BUCKET)

    # Initialize database and create tables
    setup_database(dry_run)

    # Process each language (or just the specified one)
    languages_to_process = [language_code] if language_code else SUPPORTED_LANGUAGES
    if language_code and language_code not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Language code '{language_code}' is not in SUPPORTED_LANGUAGES"
        )

    # Track overall statistics
    total_stats = {
        "lemmas": {"processed": 0, "successful": 0},
        "sentences": {"processed": 0, "successful": 0},
        "phrases": {"processed": 0, "successful": 0},
        "wordforms": {"processed": 0, "successful": 0},
        "relationships": {
            "lemma_sentences": 0,
            "phrase_sentences": 0,
            "related_phrases": 0,
        },
    }

    for lang_code in languages_to_process:
        lang_name = get_language_name(lang_code)
        logger.info(f"\nProcessing language: {lang_name} ({lang_code})")

        # Define the directories for each type
        dirs = {
            "lemmas": f"metadata/{lang_name}/lemmas",
            "sentences": f"metadata/{lang_name}/sentences",
            "phrases": f"metadata/{lang_name}/phrases",
            "wordforms": f"metadata/{lang_name}/wordforms",
        }

        # Process each type
        for data_type, directory in dirs.items():
            logger.info(f"\nProcessing {data_type}...")
            json_files = list_blobs(
                bucket_name=bucket_name,
                prefix=directory,
                pattern="*.json",
            )
            logger.info(f"Found {len(json_files)} {data_type} files")

            processed = 0
            successful = 0

            # Choose the appropriate processing function
            process_func = {
                "lemmas": process_lemma_file,
                "sentences": process_sentence_file,
                "phrases": process_phrase_file,
                "wordforms": process_wordform_file,
            }[data_type]

            for json_path in json_files:
                processed += 1
                if record := process_func(json_path, lang_code, bucket_name, dry_run):
                    successful += 1

                if processed % 100 == 0:
                    logger.info(f"Processed {processed} {data_type} files...")

            logger.info(f"Completed {data_type}: {successful}/{processed} successful")

            # Update overall statistics
            total_stats[data_type]["processed"] += processed
            total_stats[data_type]["successful"] += successful

    # Log final statistics
    logger.info("\nFinal Import Statistics:")
    for data_type, stats in total_stats.items():
        if data_type != "relationships":
            logger.info(f"{data_type.title()}:")
            logger.info(f"  Processed: {stats['processed']}")
            logger.info(f"  Successful: {stats['successful']}")

    # Log relationship statistics
    if not dry_run:
        total_stats["relationships"][
            "lemma_sentences"
        ] = LemmaExampleSentence.select().count()
        total_stats["relationships"][
            "phrase_sentences"
        ] = PhraseExampleSentence.select().count()
        total_stats["relationships"]["related_phrases"] = RelatedPhrase.select().count()

        logger.info("\nRelationships Created:")
        logger.info(
            f"  Lemma-Sentence Examples: {total_stats['relationships']['lemma_sentences']}"
        )
        logger.info(
            f"  Phrase-Sentence Examples: {total_stats['relationships']['phrase_sentences']}"
        )
        logger.info(
            f"  Related Phrases: {total_stats['relationships']['related_phrases']}"
        )

    logger.info("\nImport completed!")
    logger.info(f"Full log available in: {log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import all data from Google Cloud Storage"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without making changes"
    )
    parser.add_argument(
        "--language", help="Two-letter language code to process (e.g. 'it' for Italian)"
    )
    args = parser.parse_args()

    import_all_from_gcs(dry_run=args.dry_run, language_code=args.language)
