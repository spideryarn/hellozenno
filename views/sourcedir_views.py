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
)

sourcedir_views_bp = Blueprint("sourcedir_views", __name__, url_prefix="/lang")


@sourcedir_views_bp.route("/<target_language_code>/", strict_slashes=False)
def sourcedirs_for_language_vw(target_language_code: str):
    """Display all source directories."""
    sort_by = request.args.get("sort", "date")  # Default to recently modified
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
        sourcedirs.append({"path": sourcedir.path, "slug": sourcedir.slug})

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
            "path": sourcedir.path,
        }

    # Import here to avoid circular imports
    from views.core_views import languages_vw
    from views.wordform_views import wordforms_list_vw
    from views.lemma_views import lemmas_list_vw
    from views.phrase_views import phrases_list_vw
    from views.sentence_views import sentences_list_vw
    from views.flashcard_views import flashcard_landing_vw

    return render_template(
        "sourcedirs.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        sourcedirs=sourcedirs,
        empty_sourcedirs=empty_sourcedirs,
        current_sort=sort_by,
        supported_languages=supported_languages,
        sourcedir_stats=sourcedir_stats,
        languages_vw=languages_vw,
        sourcefiles_for_sourcedir_vw=sourcefiles_for_sourcedir_vw,
        sourcedirs_for_language_vw=sourcedirs_for_language_vw,
        wordforms_list_vw=wordforms_list_vw,
        lemmas_list_vw=lemmas_list_vw,
        phrases_list_vw=phrases_list_vw,
        sentences_list_vw=sentences_list_vw,
        flashcard_landing_vw=flashcard_landing_vw,
    )


@sourcedir_views_bp.route("/<target_language_code>/<sourcedir_slug>")
def sourcefiles_for_sourcedir_vw(target_language_code: str, sourcedir_slug: str):
    """Display all source files in a directory."""
    target_language_name = get_language_name(target_language_code)

    # Get supported languages for the dropdown
    supported_languages = get_all_languages()

    try:
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
                }
            )

        # Check if any sourcefile has vocabulary
        has_vocabulary = any(sf["metadata"]["wordform_count"] > 0 for sf in sourcefiles)

        return render_template(
            "sourcefiles.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sourcedir_path=sourcedir_entry.path,  # Use path for display
            sourcedir_slug=sourcedir_slug,  # Use slug for URL generation
            sourcedir_description=sourcedir_entry.description,  # Pass description to template
            sourcefiles=sourcefiles,
            supported_languages=supported_languages,
            has_vocabulary=has_vocabulary,
        )
    except DoesNotExist:
        # Return empty JSON array for nonexistent directories
        return "[]", 200, {"Content-Type": "application/json"}
