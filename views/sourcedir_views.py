from flask import (
    Blueprint,
    render_template,
    request,
)
from peewee import fn, DoesNotExist

from utils.lang_utils import get_language_name, get_all_languages
from db_models import (
    Sourcedir,
    Sourcefile,
    SourcefilePhrase,
)
from utils.sourcedir_utils import (
    _get_sourcedir_entry,
    get_sourcedirs_for_language,
    get_sourcefiles_for_sourcedir,
)

sourcedir_views_bp = Blueprint("sourcedir_views", __name__, url_prefix="/lang")


@sourcedir_views_bp.route("/<target_language_code>/", strict_slashes=False)
def sourcedirs_for_language_vw(target_language_code: str):
    """Display all source directories."""
    sort_by = request.args.get("sort", "date")  # Default to recently modified

    # Use the utility function to get all data
    result = get_sourcedirs_for_language(target_language_code, sort_by)

    return render_template(
        "sourcedirs.jinja",
        target_language_code=result["target_language_code"],
        target_language_name=result["target_language_name"],
        sourcedirs=result["sourcedirs"],
        empty_sourcedirs=result["empty_sourcedirs"],
        current_sort=sort_by,
        supported_languages=result["supported_languages"],
        sourcedir_stats=result["sourcedir_stats"],
    )


@sourcedir_views_bp.route("/<target_language_code>/<sourcedir_slug>")
def sourcefiles_for_sourcedir_vw(target_language_code: str, sourcedir_slug: str):
    """Display all source files in a directory."""
    try:
        # Use the utility function to get data
        result = get_sourcefiles_for_sourcedir(target_language_code, sourcedir_slug)

        # Extract values from result
        sourcedir_entry = result["sourcedir"]

        return render_template(
            "sourcefiles.jinja",
            target_language_code=target_language_code,
            target_language_name=result["target_language_name"],
            sourcedir_path=sourcedir_entry.path,  # Use path for display
            sourcedir_slug=sourcedir_slug,  # Use slug for URL generation
            sourcedir_description=sourcedir_entry.description,  # Pass description to template
            sourcefiles=result["sourcefiles"],
            supported_languages=result["supported_languages"],
            has_vocabulary=result["has_vocabulary"],
        )
    except DoesNotExist:
        # Return 404 for nonexistent directories
        return render_template("404.jinja", message="Source directory not found"), 404
