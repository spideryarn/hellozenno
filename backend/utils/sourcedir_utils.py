from flask import abort, redirect, url_for
from peewee import DoesNotExist, fn
from config import (
    SOURCE_EXTENSIONS,
)
from db_models import Sourcedir, Sourcefile, SourcefilePhrase
from utils.url_registry import endpoint_for
from utils.lang_utils import get_language_name, get_all_languages


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        ext.lstrip(".") for ext in SOURCE_EXTENSIONS
    }


def _get_sourcedir_entry(target_language_code: str, sourcedir_slug: str) -> Sourcedir:
    """Helper function to get sourcedir entry by slug with language code."""
    return Sourcedir.get(
        Sourcedir.slug == sourcedir_slug,
        Sourcedir.target_language_code == target_language_code,
    )


def _navigate_sourcefile(
    target_language_code: str,
    sourcedir_slug: str,
    sourcefile_slug: str,
    increment: int,
):
    """Core navigation function that handles both next (+1) and previous (-1) navigation."""
    from views.sourcedir_views import sourcefiles_for_sourcedir_vw
    from views.sourcefile_views import inspect_sourcefile_vw

    try:
        # Get the sourcedir entry
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Get all sourcefiles ordered by filename (case-insensitive)
        sourcefiles = (
            Sourcefile.select()
            .where(Sourcefile.sourcedir == sourcedir_entry)
            .order_by(fn.LOWER(Sourcefile.filename))
        )

        # Convert to list for easier manipulation
        slugs = [sf.slug for sf in sourcefiles]

        try:
            current_index = slugs.index(sourcefile_slug)
            target_index = current_index + increment

            if 0 <= target_index < len(slugs):
                # Valid navigation
                target_slug = slugs[target_index]
            else:
                # At boundary (first/last file), stay on current page
                target_slug = sourcefile_slug

            return redirect(
                url_for(
                    endpoint_for(inspect_sourcefile_vw),
                    target_language_code=target_language_code,
                    sourcedir_slug=sourcedir_slug,
                    sourcefile_slug=target_slug,
                )
            )
        except ValueError:
            # File not found, go back to directory
            return redirect(
                url_for(
                    endpoint_for(sourcefiles_for_sourcedir_vw),
                    target_language_code=target_language_code,
                    sourcedir_slug=sourcedir_slug,
                )
            )

    except DoesNotExist:
        abort(404)


def _get_navigation_info(sourcedir: Sourcedir, sourcefile_slug: str) -> dict:
    """Get navigation info for a sourcefile.

    Args:
        sourcedir: The Sourcedir model instance
        sourcefile_slug: The slug of the current sourcefile

    Returns a dict with:
    - is_first: bool indicating if this is the first file
    - is_last: bool indicating if this is the last file
    - total_files: total number of files in the directory
    - current_position: 1-based position of current file
    - prev_slug: slug of the previous file (if any)
    - next_slug: slug of the next file (if any)
    - first_slug: slug of the first file
    - last_slug: slug of the last file
    - sourcedir_path: the path of the sourcedir
    - prev_filename: filename of the previous file (if any)
    - next_filename: filename of the next file (if any)
    - first_filename: filename of the first file
    - last_filename: filename of the last file
    """
    # Get all sourcefiles ordered by filename (case-insensitive)
    sourcefiles = list(
        Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir)
        .order_by(fn.LOWER(Sourcefile.filename))
    )

    total_files = len(sourcefiles)

    if total_files == 0:
        return {
            "is_first": True,
            "is_last": True,
            "total_files": 0,
            "current_position": 0,
            "first_slug": None,
            "last_slug": None,
            "sourcedir_path": sourcedir.path,
            "prev_filename": None,
            "next_filename": None,
            "first_filename": None,
            "last_filename": None,
        }

    try:
        # Convert to dictionaries with slug and filename for easier manipulation
        file_info = [{"slug": sf.slug, "filename": sf.filename} for sf in sourcefiles]

        # Get slugs for compatibility
        slugs = [info["slug"] for info in file_info]

        # Get first and last info
        first_info = file_info[0] if file_info else None
        last_info = file_info[-1] if file_info else None

        first_slug = first_info["slug"] if first_info else None
        last_slug = last_info["slug"] if last_info else None
        first_filename = first_info["filename"] if first_info else None
        last_filename = last_info["filename"] if last_info else None

        # Find the current file's position in the ordered list
        current_index = slugs.index(sourcefile_slug)
        current_position = current_index + 1

        # Determine previous and next info
        prev_info = file_info[current_index - 1] if current_index > 0 else None
        next_info = (
            file_info[current_index + 1] if current_index < total_files - 1 else None
        )

        prev_slug = prev_info["slug"] if prev_info else None
        next_slug = next_info["slug"] if next_info else None
        prev_filename = prev_info["filename"] if prev_info else None
        next_filename = next_info["filename"] if next_info else None

        return {
            "is_first": current_position == 1,
            "is_last": current_position == total_files,
            "total_files": total_files,
            "current_position": current_position,
            "prev_slug": prev_slug,
            "next_slug": next_slug,
            "first_slug": first_slug,
            "last_slug": last_slug,
            "sourcedir_path": sourcedir.path,
            "prev_filename": prev_filename,
            "next_filename": next_filename,
            "first_filename": first_filename,
            "last_filename": last_filename,
        }
    except (ValueError, IndexError):
        # File not found
        return {
            "is_first": True,
            "is_last": True,
            "total_files": total_files,
            "current_position": 0,
            "sourcedir_path": sourcedir.path,
            "first_slug": first_slug if "first_slug" in locals() else None,
            "last_slug": last_slug if "last_slug" in locals() else None,
            "first_filename": first_filename if "first_filename" in locals() else None,
            "last_filename": last_filename if "last_filename" in locals() else None,
        }


def get_sourcedir_or_404(target_language_code: str, sourcedir_slug: str) -> Sourcedir:
    """Get sourcedir by language code and slug, or return 404."""
    try:
        return _get_sourcedir_entry(target_language_code, sourcedir_slug)
    except DoesNotExist:
        abort(404, description="Source directory not found")


def get_sourcedirs_for_language(target_language_code: str, sort_by: str = "date"):
    """
    Get all sourcedirs for a specific language with statistics.

    Args:
        target_language_code: Language code to filter by
        sort_by: How to sort results - 'date' (default) or 'alpha'

    Returns:
        A dictionary with the following keys:
        - target_language_code: The language code
        - target_language_name: The language name
        - sourcedirs: List of sourcedir info dictionaries
        - empty_sourcedirs: List of slugs for empty sourcedirs
        - sourcedir_stats: Dictionary of statistics keyed by sourcedir slug
    """
    target_language_name = get_language_name(target_language_code)

    # Get supported languages for the dropdown
    supported_languages = get_all_languages()

    # Query sourcedirs from database - filtered by language
    query = Sourcedir.select().where(
        Sourcedir.target_language_code == target_language_code
    )

    if sort_by == "date":
        # Sort by modification time, newest first
        query = query.order_by(
            fn.COALESCE(Sourcedir.updated_at, Sourcedir.created_at).desc()
        )
    else:
        # Default alphabetical sort
        query = query.order_by(Sourcedir.path)

    # Get all sourcedirs and check which ones are empty
    sourcedirs = []
    empty_sourcedirs = []
    sourcedir_stats = {}

    for sourcedir in query:
        sourcedirs.append(
            {
                "path": sourcedir.path,
                "slug": sourcedir.slug,
                "description": sourcedir.description,
                "created_at": sourcedir.created_at,
                "updated_at": sourcedir.updated_at,
                "created_by_id": sourcedir.created_by_id,
            }
        )

        # Count sourcefiles
        sourcefile_count = (
            Sourcefile.select().where(Sourcefile.sourcedir == sourcedir).count()
        )
        if sourcefile_count == 0:
            empty_sourcedirs.append(sourcedir.slug)

        # Count phrases
        phrase_count = (
            SourcefilePhrase.select()
            .join(Sourcefile)
            .where(Sourcefile.sourcedir == sourcedir)
            .count()
        )

        sourcedir_stats[sourcedir.slug] = {
            "phrase_count": phrase_count,
            "file_count": sourcefile_count,
            "path": sourcedir.path,
        }

    return {
        "target_language_code": target_language_code,
        "target_language_name": target_language_name,
        "sourcedirs": sourcedirs,
        "empty_sourcedirs": empty_sourcedirs,
        "sourcedir_stats": sourcedir_stats,
        "supported_languages": supported_languages,
    }


def get_sourcefiles_for_sourcedir(target_language_code: str, sourcedir_slug: str):
    """
    Get all sourcefiles for a specific sourcedir with metadata.

    Args:
        target_language_code: Language code to filter by
        sourcedir_slug: Slug of the sourcedir to get files from

    Returns:
        A dictionary with the following keys:
        - sourcedir: The sourcedir entry
        - sourcefiles: List of sourcefile info dictionaries
        - target_language_name: The language name
        - has_vocabulary: Boolean indicating if any file has vocabulary
        - supported_languages: List of supported languages
    """
    from utils.lang_utils import get_language_name, get_all_languages
    from db_models import Sourcefile
    from peewee import fn, DoesNotExist

    target_language_name = get_language_name(target_language_code)

    # Get supported languages for the dropdown
    supported_languages = get_all_languages()

    # Get the sourcedir entry by slug
    sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

    # Get all sourcefiles for this directory
    sourcefiles = []
    for sourcefile_entry in (
        Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir_entry)
        .order_by(fn.LOWER(Sourcefile.filename))
    ):
        # Count wordforms and phrases
        wordform_count = sourcefile_entry.wordform_entries.count()
        phrase_count = sourcefile_entry.phrase_entries.count()

        # Prepare metadata for each file
        metadata = {
            "created_at": sourcefile_entry.created_at,
            "updated_at": sourcefile_entry.updated_at,
            "has_audio": sourcefile_entry.audio_data is not None,
            "wordform_count": wordform_count,
            "phrase_count": phrase_count,
        }
        if sourcefile_entry.metadata:
            if "image_processing" in sourcefile_entry.metadata:
                metadata["image_processing"] = sourcefile_entry.metadata[
                    "image_processing"
                ]
            if "duration" in sourcefile_entry.metadata:
                metadata["duration"] = sourcefile_entry.metadata["duration"]
            if "video_title" in sourcefile_entry.metadata:
                metadata["video_title"] = sourcefile_entry.metadata["video_title"]

        sourcefiles.append(
            {
                "filename": sourcefile_entry.filename,
                "slug": sourcefile_entry.slug,
                "sourcefile_type": sourcefile_entry.sourcefile_type,
                "metadata": metadata,
                "created_by_id": sourcefile_entry.created_by_id,
                "updated_at": sourcefile_entry.updated_at,
                "ai_generated": sourcefile_entry.ai_generated
            }
        )

    # Check if any sourcefile has vocabulary
    has_vocabulary = any(sf["metadata"]["wordform_count"] > 0 for sf in sourcefiles)

    return {
        "sourcedir": sourcedir_entry,
        "sourcefiles": sourcefiles,
        "target_language_name": target_language_name,
        "has_vocabulary": has_vocabulary,
        "supported_languages": supported_languages,
    }
