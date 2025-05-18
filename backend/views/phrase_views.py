from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from db_models import Phrase
from peewee import DoesNotExist, fn
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import extract_phrases_from_text
from utils.phrase_utils import get_phrases_query, get_phrase_by_slug
from slugify import slugify

phrase_views_bp = Blueprint("phrase_views", __name__, url_prefix="/language")


@phrase_views_bp.route("/<target_language_code>/phrases")
def phrases_list_vw(target_language_code):
    """Show list of phrases for a language."""
    sort_by = request.args.get("sort", "alpha")  # Default to alphabetical
    target_language_name = get_language_name(target_language_code)

    # Get the query using the shared utility function
    query = get_phrases_query(target_language_code, sort_by)

    return render_template(
        "phrases.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        phrases=query,
        current_sort=sort_by,
    )


@phrase_views_bp.route("/<target_language_code>/phrase/<slug>")
def get_phrase_metadata_vw(target_language_code: str, slug: str):
    """Get metadata for a specific phrase using its slug."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Use the utility function to find phrase by slug
        phrase = get_phrase_by_slug(target_language_code, slug)
    except DoesNotExist:
        abort(404, description=f"Phrase with slug '{slug}' not found")

    # Prepare metadata for template
    metadata = {
        "created_at": phrase.created_at,
        "updated_at": phrase.updated_at,
    }

    return render_template(
        "phrase.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        phrase=phrase,
        metadata=metadata,  # Add metadata to template context
    )


@phrase_views_bp.route(
    "/<target_language_code>/phrases/<slug>/delete", methods=["POST"]
)
def delete_phrase_vw(target_language_code, slug):
    """Delete a specific phrase using its slug."""
    try:
        phrase = get_phrase_by_slug(target_language_code, slug)
        # phrase_text = phrase.canonical_form # Not needed if not flashing
        phrase.delete_instance()
        # flash(f"Phrase '{phrase_text}' has been deleted.", "success") # Flashing is for Jinja templates
    except DoesNotExist:
        # If it doesn't exist, it's already gone. Client can treat as success.
        pass  # Fall through to return 204

    # Return 204 No Content for successful deletion or if already deleted
    return "", 204
