"""Script for importing sourcedirs and sourcefiles from local filesystem."""

import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Union, Tuple
import logging
from datetime import datetime
import json
import glob


from utils.db_connection import database, init_db
from db_models import Sourcedir, Sourcefile
from utils.logging_utils import setup_logging


PathLike = Union[str, Path]


def read_file(path: PathLike) -> bytes:
    """Read a file as bytes."""
    with open(path, "rb") as f:
        return f.read()


def read_json_file(path: PathLike) -> dict:
    """Read a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def setup_database(dry_run: bool) -> None:
    """Initialize database and create tables."""
    init_db()
    logger = setup_logging()
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Database initialized")

    if not dry_run:
        with database:
            # Drop tables in reverse order
            database.drop_tables([Sourcefile, Sourcedir], safe=True)
            logger.info("Dropped existing tables")

            # Create tables in correct order
            database.create_tables([Sourcedir, Sourcefile])
            logger.info("Created tables")


def create_or_get_sourcedir(
    path: str, dry_run: bool
) -> Tuple[Optional[Sourcedir], bool]:
    """Create or get a sourcedir entry."""
    logger = setup_logging()

    try:
        if not dry_run:
            sourcedir_entry, created = Sourcedir.get_or_create(path=path)
            logger.debug(f"{'Created' if created else 'Found'} sourcedir: {path}")
            return sourcedir_entry, True
        else:
            logger.debug(f"[DRY RUN] Would create/get sourcedir: {path}")
            return None, True
    except Exception as e:
        logger.error(f"Error processing sourcedir {path}: {str(e)}")
        return None, False


def process_sourcefile(
    file_path: Path,
    sourcedir_entry: Optional[Sourcedir],
    base_path: Path,
    dry_run: bool,
) -> Optional[Dict[str, Any]]:
    """Process a single sourcefile."""
    logger = setup_logging()
    try:
        # Get the metadata JSON
        json_path = file_path.with_suffix(".json")
        if not json_path.exists():
            logger.warning(f"No JSON metadata found for {file_path}")
            return None

        metadata = read_json_file(json_path)
        logger.debug(f"Read metadata from {json_path}")

        # Extract required text fields
        text_target = metadata["source"]["txt_tgt"]
        text_english = metadata["source"]["txt_en"]
        audio_filename = metadata["source"].get("txt_tgt_mp3_filen")
        logger.debug(f"Extracted text fields. Audio filename: {audio_filename}")

        # Get image data
        image_data = read_file(file_path)
        logger.debug(f"Read image data: {len(image_data)} bytes")

        # Get audio data if it exists and has a filename
        audio_data = None
        if audio_filename:
            try:
                audio_path = Path(audio_filename)
                if not audio_path.is_absolute():
                    # If relative path, make it relative to base_path
                    audio_path = base_path / audio_path
                audio_data = read_file(audio_path)
                logger.debug(f"Read audio data: {len(audio_data)} bytes")
            except Exception as e:
                logger.warning(f"Could not read audio file {audio_filename}: {str(e)}")

        # Get paths relative to sourcefiles directory
        relative_file_path = file_path.relative_to(base_path)
        relative_dir_path = str(relative_file_path.parent)
        logger.debug(
            f"Relative paths - dir: {relative_dir_path}, file: {relative_file_path.name}"
        )

        if not dry_run:
            # Create or update the sourcefile entry
            sourcefile_entry, created = Sourcefile.get_or_create(
                sourcedir=sourcedir_entry,
                filename=relative_file_path.name,
                defaults={
                    "image_data": image_data,
                    "audio_data": audio_data,
                    "text_target": text_target,
                    "text_english": text_english,
                    "audio_filename": audio_filename,
                    "metadata": metadata,
                },
            )

            if not created:
                # Update existing entry
                sourcefile_entry.image_data = image_data
                sourcefile_entry.audio_data = audio_data
                sourcefile_entry.text_target = text_target
                sourcefile_entry.text_english = text_english
                sourcefile_entry.audio_filename = audio_filename
                sourcefile_entry.metadata = metadata
                sourcefile_entry.save()

            logger.debug(
                f"{'Created' if created else 'Updated'} sourcefile: {relative_file_path}"
            )
        else:
            logger.debug(
                f"[DRY RUN] Would create/update sourcefile: {relative_file_path}"
            )

        return metadata

    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return None


def import_sourcedirs_sourcefiles(base_path: PathLike, dry_run: bool = False) -> None:
    """Import all sourcedirs and sourcefiles from local filesystem."""
    # Set up logging
    logger = setup_logging()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"import_sourcedirs_sourcefiles_log_{timestamp}.txt"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    logger.info(f"Starting import from {base_path}")
    logger.info(f"Log file: {log_file}")

    # Initialize database and create tables
    setup_database(dry_run)

    # Track statistics
    stats = {
        "sourcedirs": {"processed": 0, "successful": 0},
        "sourcefiles": {"processed": 0, "successful": 0},
    }

    base_path = Path(base_path)

    # Find all image files (jpg, jpeg, png)
    patterns = ["*.jpg", "*.jpeg", "*.png"]
    source_files = []
    for pattern in patterns:
        found_files = list(base_path.rglob(pattern))
        logger.info(f"Found {len(found_files)} files matching pattern {pattern}")
        source_files.extend(found_files)

    logger.info(f"Total files found: {len(source_files)}")

    # Process each sourcefile
    for source_file in source_files:
        source_path = Path(source_file)
        relative_dir_path = str(source_path.parent.relative_to(base_path))
        logger.debug(f"\nProcessing file: {source_path}")
        logger.debug(f"Relative directory: {relative_dir_path}")

        # Create or get sourcedir
        sourcedir_entry, success = create_or_get_sourcedir(relative_dir_path, dry_run)
        stats["sourcedirs"]["processed"] += 1
        if success:
            stats["sourcedirs"]["successful"] += 1

            # Process the sourcefile
            stats["sourcefiles"]["processed"] += 1
            if process_sourcefile(source_path, sourcedir_entry, base_path, dry_run):
                stats["sourcefiles"]["successful"] += 1

        if stats["sourcefiles"]["processed"] % 10 == 0:
            logger.info(
                f"Processed {stats['sourcefiles']['processed']}/{len(source_files)} sourcefiles..."
            )

    # Log final statistics
    logger.info("\nFinal Import Statistics:")
    for data_type, counts in stats.items():
        logger.info(f"\n{data_type.title()}:")
        logger.info(f"  Processed: {counts['processed']}")
        logger.info(f"  Successful: {counts['successful']}")

    logger.info("\nImport completed!")
    logger.info(f"Full log available in: {log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import sourcedirs and sourcefiles from local filesystem"
    )
    parser.add_argument(
        "base_path",
        help="Base path containing the sourcefiles directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes",
    )
    args = parser.parse_args()

    import_sourcedirs_sourcefiles(args.base_path, dry_run=args.dry_run)
