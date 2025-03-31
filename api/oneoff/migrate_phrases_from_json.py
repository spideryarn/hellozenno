#!/usr/bin/env python3
"""Migrate phrases from Sourcefile.metadata JSON to Phrase and SourcefilePhrase tables."""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from db_models import Sourcedir, Sourcefile, Phrase, SourcefilePhrase
from utils.db_connection import get_db_config, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_phrases():
    """Migrate phrases from JSON metadata to proper tables."""
    # Initialize database connection
    database = get_db_config()
    init_db()

    with database.atomic():
        # Count total sourcefiles for progress tracking
        total_files = Sourcefile.select().count()
        processed_files = 0
        phrases_migrated = 0

        for sourcefile in Sourcefile.select().join(Sourcedir):
            processed_files += 1
            metadata = sourcefile.metadata
            if not metadata or "phrases" not in metadata:
                logger.info(
                    f"[{processed_files}/{total_files}] No phrases in {sourcefile.filename}"
                )
                continue

            logger.info(
                f"[{processed_files}/{total_files}] Processing {len(metadata['phrases'])} phrases from {sourcefile.filename}"
            )

            for phrase_data in metadata["phrases"]:
                # Create or get the phrase
                now = datetime.now()
                phrase, created = Phrase.get_or_create(
                    canonical_form=phrase_data["canonical_form"],
                    language_code=sourcefile.sourcedir.language_code,  # Get language from sourcedir
                    defaults={
                        "raw_forms": phrase_data.get("raw_forms", []),
                        "translations": phrase_data.get("translations", []),
                        "part_of_speech": phrase_data.get("part_of_speech", "unknown"),
                        "register": phrase_data.get("register"),
                        "commonality": phrase_data.get("commonality"),
                        "guessability": phrase_data.get("guessability"),
                        "etymology": phrase_data.get("etymology"),
                        "cultural_context": phrase_data.get("cultural_context"),
                        "mnemonics": phrase_data.get("mnemonics"),
                        "component_words": phrase_data.get("component_words"),
                        "usage_notes": phrase_data.get("usage_notes"),
                        "difficulty_level": phrase_data.get("difficulty_level"),
                        "created_at": now,
                        "updated_at": now,
                    },
                )

                # Create the link
                _, created = SourcefilePhrase.get_or_create(
                    sourcefile=sourcefile,
                    phrase=phrase,
                    defaults={
                        "centrality": phrase_data.get("centrality"),
                        "ordering": phrase_data.get("ordering"),
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                phrases_migrated += 1

            # Remove phrases from JSON metadata
            metadata["phrases"] = []
            sourcefile.metadata = metadata
            sourcefile.save()

        logger.info(
            f"Migration complete. Processed {processed_files} files, migrated {phrases_migrated} phrases."
        )


if __name__ == "__main__":
    migrate_phrases()
