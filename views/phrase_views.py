from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from db_models import Phrase
from peewee import DoesNotExist, fn
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import extract_phrases_from_text
from slugify import slugify

phrase_views_bp = Blueprint("phrase_views", __name__, url_prefix="/lang")


@phrase_views_bp.route("/<target_language_code>/phrases")
def phrases_list_vw(target_language_code):
    """Show list of phrases for a language."""
    sort_by = request.args.get("sort", "alpha")  # Default to alphabetical
    target_language_name = get_language_name(target_language_code)

    # Query phrases from database
    query = Phrase.select().where(Phrase.language_code == target_language_code)

    if sort_by == "date":
        # Sort by modification time, newest first
        query = query.order_by(fn.COALESCE(Phrase.updated_at, Phrase.created_at).desc())
    else:
        # Default alphabetical sort
        query = query.order_by(Phrase.canonical_form)

    return render_template(
        "phrases.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        phrases=query,
        current_sort=sort_by,
    )


@phrase_views_bp.route("/<target_language_code>/phrases/<slug>")
def get_phrase_metadata_vw(target_language_code, slug):
    """Get metadata for a specific phrase using its slug."""
    target_language_name = get_language_name(target_language_code)

    try:
        # First try to find existing phrase in database by slug
        phrase = Phrase.get(
            (Phrase.language_code == target_language_code) & (Phrase.slug == slug)
        )
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
        phrase = Phrase.get(
            (Phrase.language_code == target_language_code) & (Phrase.slug == slug)
        )
        phrase_text = phrase.canonical_form
        phrase.delete_instance()
        flash(f"Phrase '{phrase_text}' has been deleted.", "success")
    except DoesNotExist:
        abort(404, description=f"Phrase with slug '{slug}' not found")

    return redirect(
        url_for(
            "phrase_views.phrases_list_vw", target_language_code=target_language_code
        )
    )
