from db_models import Sentence, Sourcedir, Sourcefile, SourcefileWordform, Wordform
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_random_sentence
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas, normalize_text
from utils.vocab_llm_utils import extract_tokens, create_interactive_word_data
from utils.flashcard_utils import (
    get_flashcard_landing_data,
    get_flashcard_sentence_data,
    get_random_flashcard_data,
)
from views.flashcard_views import flashcard_views_bp

# Import auth decorator
from utils.auth_utils import api_auth_optional

from flask import jsonify, request, url_for, Blueprint
from peewee import DoesNotExist

# Create a separate blueprint for API endpoints
flashcard_api_bp = Blueprint("flashcard_api", __name__, url_prefix="/api/lang")


@flashcard_api_bp.route(
    "/<target_language_code>/flashcards/sentence/<slug>", methods=["GET"]
)
@api_auth_optional  # Auth is optional here
def flashcard_sentence_api(target_language_code: str, slug: str):
    """JSON API endpoint for a specific sentence."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_sentence_data(
        target_language_code=target_language_code,
        slug=slug,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        status_code = data.get("status_code", 404)
        error_body = {k: v for k, v in data.items() if k in ("error", "error_code", "details")}
        if "error" not in error_body and isinstance(data.get("error"), str):
            error_body["error"] = data["error"]
        return jsonify(error_body), status_code

    # Remove the sentence model from the API response
    if "sentence" in data:
        del data["sentence"]

    return jsonify(data)


@flashcard_api_bp.route("/<target_language_code>/flashcards/random", methods=["GET"])
@api_auth_optional  # Auth is optional here
def random_flashcard_api(target_language_code: str):
    """JSON API endpoint for a random sentence."""
    from loguru import logger

    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    logger.info(
        f"Fetching random flashcard: language={target_language_code}, sourcefile={sourcefile_slug}, sourcedir={sourcedir_slug}"
    )

    # Get profile from flask g object if available
    profile = None
    from flask import g

    if hasattr(g, "profile") and g.profile:
        profile = g.profile

    # Use the shared utility function
    data = get_random_flashcard_data(
        target_language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
        profile=profile,
    )

    # Handle error responses with proper status codes
    if "error" in data:
        status_code = data.get("status_code", 404)
        # Log the error with appropriate level based on status code
        if status_code >= 500:
            logger.error(
                f"Error getting random flashcard: {data.get('error')} ({data.get('error_code')})"
            )
        else:
            logger.warning(
                f"Issue getting random flashcard: {data.get('error')} ({data.get('error_code')})"
            )

        error_body = {k: v for k, v in data.items() if k in ("error", "error_code", "details")}
        if "error" not in error_body and isinstance(data.get("error"), str):
            error_body["error"] = data["error"]
        return jsonify(error_body), status_code

    # Keep the random endpoint lightweight; return minimal routing info
    response_data = {
        "id": data.get("id"),
        "slug": data.get("slug"),
        "metadata": {
            "target_language_code": target_language_code,
            "language_name": get_language_name(target_language_code),
        },
    }
    if sourcefile_slug:
        response_data["metadata"]["sourcefile"] = sourcefile_slug
    if sourcedir_slug:
        response_data["metadata"]["sourcedir"] = sourcedir_slug

    logger.info(
        f"Successfully retrieved random flashcard with sentence ID {response_data.get('id')}"
    )
    return jsonify(response_data)


@flashcard_api_bp.route("/<target_language_code>/flashcards/landing", methods=["GET"])
def flashcard_landing_api(target_language_code: str):
    """JSON API endpoint for the flashcard landing page."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_landing_data(
        target_language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        status_code = data.get("status_code", 404)
        error_body = {k: v for k, v in data.items() if k in ("error", "error_code", "details")}
        if "error" not in error_body and isinstance(data.get("error"), str):
            error_body["error"] = data["error"]
        return jsonify(error_body), status_code

    return jsonify(data)
