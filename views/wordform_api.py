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
        language_code=target_language_code, sort_by=sort_by
    )

    # Convert to list of dictionaries for JSON serialization
    wordforms_data = [wordform.to_dict() for wordform in wordforms]

    return jsonify(wordforms_data)


@wordform_api_bp.route("/<target_language_code>/wordform/<wordform>")
def get_wordform_metadata_api(target_language_code: str, wordform: str):
    """Get metadata for a wordform and its lemma.

    This API endpoint corresponds to the get_wordform_metadata_vw view function.
    It returns complete metadata for a wordform, including its lemma if available.
    """
    # URL decode the wordform parameter to handle non-Latin characters properly
    wordform = urllib.parse.unquote(wordform)

    try:
        # Get the metadata using the utility function
        result = get_wordform_metadata(target_language_code, wordform)

        # Split the inflection_type string into a list if it exists
        if (
            result["wordform_metadata"]
            and "inflection_type" in result["wordform_metadata"]
            and result["wordform_metadata"]["inflection_type"]
        ):
            inflection_type = result["wordform_metadata"]["inflection_type"]
            if isinstance(inflection_type, str):
                result["wordform_metadata"]["inflection_types"] = [
                    inflection_type.strip()
                    for inflection_type in inflection_type.split()
                    if inflection_type.strip()
                ]

        return jsonify(result)
    except DoesNotExist:
        response_data = {
            "error": "Not Found",
            "description": f"Wordform '{wordform}' not found",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
        }
        response = jsonify(response_data)
        response.status_code = 404
        return response
