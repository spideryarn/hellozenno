from flask import abort, redirect, url_for
from peewee import DoesNotExist
from config import (
    SOURCE_EXTENSIONS,
)
from db_models import Sourcedir, Sourcefile


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
    try:
        # Get the sourcedir entry
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Get all sourcefiles ordered by filename
        sourcefiles = (
            Sourcefile.select()
            .where(Sourcefile.sourcedir == sourcedir_entry)
            .order_by(Sourcefile.filename)
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
                    "sourcefile_views.inspect_sourcefile",
                    target_language_code=target_language_code,
                    sourcedir_slug=sourcedir_slug,
                    sourcefile_slug=target_slug,
                )
            )
        except ValueError:
            # File not found, go back to directory
            return redirect(
                url_for(
                    "sourcedir_views.sourcefiles_for_sourcedir",
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
    # Get all sourcefiles ordered by filename
    sourcefiles = list(
        Sourcefile.select()
        .where(Sourcefile.sourcedir == sourcedir)
        .order_by(Sourcefile.filename)
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


def _get_sourcefile_entry(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
) -> Sourcefile:
    """Helper function to get sourcefile entry by slug with language code."""
    sourcedir = _get_sourcedir_entry(target_language_code, sourcedir_slug)
    return Sourcefile.get(
        Sourcefile.sourcedir == sourcedir,
        Sourcefile.slug == sourcefile_slug,
    )


def get_sourcedir_or_404(language_code: str, sourcedir_slug: str) -> Sourcedir:
    """Get sourcedir by language code and slug, or return 404."""
    try:
        return _get_sourcedir_entry(language_code, sourcedir_slug)
    except DoesNotExist:
        abort(404, description="Source directory not found")
