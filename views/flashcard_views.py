"""
Svelte-based flashcard system for language learning.
This is the main flashcards implementation, replacing the old vanilla JS version.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    send_from_directory,
    current_app,
)
from peewee import DoesNotExist
from typing import Dict, Any, cast

from utils.lang_utils import get_language_name
from utils.sentence_utils import get_random_sentence
from utils.audio_utils import ensure_model_audio_data
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas
from utils.flashcard_utils import (
    get_flashcard_landing_data,
    get_flashcard_sentence_data,
    get_random_flashcard_data,
)

from db_models import Sentence, Sourcefile, SourcefileWordform, Sourcedir

# Create the blueprint for flashcard views
flashcard_views_bp = Blueprint(
    "flashcard_views", __name__, url_prefix="/lang", static_folder="../static/build"
)


@flashcard_views_bp.route("/<target_language_code>/flashcards")
def flashcard_landing_vw(target_language_code: str):
    """Landing page for Svelte-based flashcards with start button."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_landing_data(
        language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        abort(404, description=data["error"])

    # Extract data for the template
    return render_template(
        "flashcard_landing.jinja",
        target_language_code=data["language_code"],
        target_language_name=data["language_name"],
        sourcefile=data["sourcefile"],
        sourcedir=data["sourcedir"],
        lemma_count=data["lemma_count"],
    )


@flashcard_views_bp.route("/<target_language_code>/flashcards/sentence/<slug>")
def flashcard_sentence_vw(target_language_code: str, slug: str):
    """View a specific sentence as a Svelte-based flashcard."""
    # Get parameters from query
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    result = get_flashcard_sentence_data(
        language_code=target_language_code,
        slug=slug,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in result:
        abort(404, description=result["error"])

    # Cast result to Dict[str, Any] to help type checking
    data = cast(Dict[str, Any], result)
    metadata = cast(Dict[str, Any], data.get("metadata", {}))
    language_name = cast(str, metadata.get("language_name", ""))

    return render_template(
        "flashcard_sentence.jinja",
        target_language_code=target_language_code,
        target_language_name=language_name,
        sentence=data["sentence"],  # Pass the full sentence model to the template
        sourcefile=data.get("sourcefile"),
        sourcedir=data.get("sourcedir"),
        lemma_count=data.get("lemma_count"),
    )


@flashcard_views_bp.route("/<target_language_code>/flashcards/random")
def random_flashcard_vw(target_language_code: str):
    """Redirect to a random sentence flashcard."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_random_flashcard_data(
        language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        abort(404, description=data["error"])

    # Preserve only sourcefile/sourcedir in redirect
    query_params = {}
    if sourcefile_slug:
        query_params["sourcefile"] = sourcefile_slug
    if sourcedir_slug:
        query_params["sourcedir"] = sourcedir_slug

    return redirect(
        url_for(
            "flashcard_views.flashcard_sentence_vw",
            target_language_code=target_language_code,
            slug=data["slug"],
            **query_params,
        )
    )
