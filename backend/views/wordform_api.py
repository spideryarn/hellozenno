"""API endpoints for word forms.

All endpoints for interacting with word forms programmatically.
These endpoints follow the standard pattern:
/api/lang/word/...
"""

from flask import Blueprint, jsonify, send_file, abort, request
from peewee import DoesNotExist
import urllib.parse

from db_models import Wordform
from utils.word_utils import get_word_preview, get_wordform_metadata
from utils.lang_utils import get_language_name

# Import auth decorator
from utils.auth_utils import api_auth_optional

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
    wordform = urllib.parse.unquote(wordform)

    # Use the shared utility function to find or create the wordform
    from utils.word_utils import find_or_create_wordform
    from loguru import logger

    logger.info(
        f"API request for wordform '{wordform}' in language '{target_language_code}'"
    )
    try:
        result = find_or_create_wordform(target_language_code, wordform)
        logger.info(f"Wordform processing complete with status: {result['status']}")

        # Handle different status responses
        if result["status"] == "found":
            # For both existing and newly created wordforms
            return jsonify(result["data"])
        elif result["status"] == "multiple_matches":
            # For multiple potential matches
            return jsonify(result["data"])
        elif result["status"] == "redirect":
            # Only used as a fallback now
            return jsonify(result["data"])
        else:  # invalid
            # For invalid wordforms
            response = jsonify(result["data"])
            response.status_code = 404
            return response

    except AuthenticationRequiredForGenerationError:
        # Handle the case where generation requires login
        error_data = {
            "error": "Authentication Required",
            "description": "Authentication required to search for or generate wordform details",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "authentication_required_for_generation": True,  # Add a flag for frontend
            "wordform": wordform,  # Include the original wordform searched
        }
        return jsonify(error_data), 401
    except Exception as e:
        logger.exception(f"Error getting wordform metadata for '{wordform}': {e}")
        return (
            jsonify({"error": "Failed to process wordform", "description": str(e)}),
            500,
        )
