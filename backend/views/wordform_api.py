"""API endpoints for word forms.

All endpoints for interacting with word forms programmatically.
These endpoints follow the standard pattern:
/api/lang/word/...
"""

from flask import Blueprint, jsonify, send_file, abort, request
from peewee import DoesNotExist
import urllib.parse
from loguru import logger

from db_models import Wordform
from utils.word_utils import get_word_preview
from utils.lang_utils import get_language_name

# Import auth decorator
from utils.auth_utils import api_auth_optional, api_auth_required

# Import exception
from utils.exceptions import AuthenticationRequiredForGenerationError

# Create a blueprint with standardized prefix
wordform_api_bp = Blueprint("wordform_api", __name__, url_prefix="/api/lang/word")


@wordform_api_bp.route("/<target_language_code>/<word>/preview")
def word_preview_api(target_language_code: str, word: str):
    """Get preview data for word tooltips."""
    # Fix URL encoding issues with Vercel by explicitly unquoting the word parameter
    word = urllib.parse.unquote(word)

    preview = get_word_preview(target_language_code, word)
    if preview is None:
        response = jsonify(
            {"error": "Not Found", "description": f"Word '{word}' not found"}
        )
        response.status_code = 404
        return response
    response = jsonify(preview)
    response.headers["Cache-Control"] = "public, max-age=60"  # Cache for 1 minute
    return response


@wordform_api_bp.route("/<target_language_code>/<word>/mp3")
def get_mp3_api(target_language_code: str, word: str):
    """Return the MP3 file for the given word."""
    mp3_filen = f"{word}.mp3"
    try:
        return send_file(mp3_filen, mimetype="audio/mpeg")
    except FileNotFoundError:
        abort(404, description="MP3 file not found")


@wordform_api_bp.route("/<target_language_code>/wordforms")
def wordforms_list_api(target_language_code: str):
    """Return all wordforms for a language.

    Returns a list of all wordforms for the specified language code.
    Each wordform includes basic metadata like wordform, translations, and part of speech.
    """
    # Get sort parameter from request
    sort_by = request.args.get("sort", "alpha")

    # Get all wordforms for this language
    wordforms = Wordform.get_all_wordforms_for(
        target_language_code=target_language_code, sort_by=sort_by
    )

    # Convert to list of dictionaries for JSON serialization
    wordforms_data = [wordform.to_dict() for wordform in wordforms]

    return jsonify(wordforms_data)


@wordform_api_bp.route("/<target_language_code>/wordform/<wordform>")
@api_auth_optional  # Generation might be needed, so check auth
def get_wordform_metadata_api(target_language_code: str, wordform: str):
    """Get metadata for a wordform and its lemma.

    This API endpoint corresponds to the get_wordform_metadata_vw view function.
    It returns complete metadata for a wordform, including its lemma if available.
    If the wordform doesn't exist, it will search for possible matches.

    The find_or_create_wordform function now synchronously waits for wordform
    generation to complete, so this endpoint may take a few seconds to respond
    when a new wordform is being created.
    """
    # URL decode the wordform parameter to handle non-Latin characters properly
    decoded_wordform = urllib.parse.unquote(wordform)
    logger.info(
        f"[Flask API] Received request for wordform: '{decoded_wordform}' (raw: '{wordform}'), lang: '{target_language_code}'"
    )

    # Use the shared utility function to find or create the wordform
    from utils.word_utils import find_or_create_wordform

    logger.info(
        f"API request for wordform '{wordform}' in language '{target_language_code}'"
    )
    try:
        result = find_or_create_wordform(target_language_code, decoded_wordform)
        logger.info(
            f"[Flask API] find_or_create_wordform for '{decoded_wordform}' returned status: {result.get('status')}. Full result: {result}"
        )

        # Handle different status responses
        response_json = jsonify(result)
        status_code = 200

        if result.get("status") == "found":
            logger.info(
                f"[Flask API] Status 'found' for '{decoded_wordform}'. Sending {status_code}."
            )
        elif result.get("status") == "multiple_matches":
            logger.info(
                f"[Flask API] Status 'multiple_matches' for '{decoded_wordform}'. Sending {status_code}."
            )
        elif result.get("status") == "redirect":
            logger.info(
                f"[Flask API] Status 'redirect' for '{decoded_wordform}'. Sending {status_code}."
            )
        elif result.get("status") == "invalid":
            status_code = 404
            logger.info(
                f"[Flask API] Status 'invalid' for '{decoded_wordform}'. Sending {status_code}."
            )
        else:
            logger.warning(
                f"[Flask API] Unknown status '{result.get('status')}' for '{decoded_wordform}'. Sending {status_code} by default. Result: {result}"
            )

        response_json.status_code = status_code
        logger.debug(
            f"[Flask API] About to send response for '{decoded_wordform}'. Status: {status_code}, Payload: {result}"
        )
        return response_json

    except AuthenticationRequiredForGenerationError as e:
        logger.warning(
            f"[Flask API] AuthenticationRequiredForGenerationError for '{decoded_wordform}': {e}"
        )
        error_data = {
            "error": "Authentication Required",
            "description": "Authentication required to search for or generate wordform details",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "authentication_required_for_generation": True,  # Add a flag for frontend
            "wordform": decoded_wordform,  # Include the original wordform searched
        }
        return jsonify(error_data), 401
    except Exception as e:
        logger.exception(
            f"[Flask API] Unhandled exception for '{decoded_wordform}': {e}"
        )
        return (
            jsonify({"error": "Failed to process wordform", "description": str(e)}),
            500,
        )


@wordform_api_bp.route(
    "/<target_language_code>/wordform/<wordform>/delete", methods=["POST"]
)
@api_auth_required
def delete_wordform_api(target_language_code: str, wordform: str):
    """Delete a wordform from the database."""
    # URL decode the wordform parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    wordform = urllib.parse.unquote(wordform)

    try:
        wordform_model = Wordform.get(
            Wordform.wordform == wordform,
            Wordform.target_language_code == target_language_code,
        )
        wordform_model.delete_instance()
        # Return 204 No Content on successful deletion
        return "", 204
    except DoesNotExist:
        # Also return 204 if it doesn't exist, as the resource is effectively gone
        return "", 204
