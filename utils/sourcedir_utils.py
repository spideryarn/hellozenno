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
        Sourcedir.language_code == target_language_code,
    )


def _navigate_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str, increment: int
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
    """
    # Get all sourcefiles ordered by filename (case-insensitive)
    sourcefiles = list(
        Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir)
        .order_by(fn.LOWER(Sourcefile.filename))
    )

    total_files = len(sourcefiles)

    try:
        # Find the current file's position in the ordered list
        current_position = next(
            i + 1 for i, sf in enumerate(sourcefiles) if sf.slug == sourcefile_slug
        )
        return {
            "is_first": current_position == 1,
            "is_last": current_position == total_files,
            "total_files": total_files,
            "current_position": current_position,
        }
    except StopIteration:
        # File not found
        return {
            "is_first": True,
            "is_last": True,
            "total_files": total_files,
            "current_position": 0,
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
    query = Sourcedir.select().where(Sourcedir.language_code == target_language_code)

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
