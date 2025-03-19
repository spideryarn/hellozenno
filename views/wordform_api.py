"""API endpoints for word forms.

All endpoints for interacting with word forms programmatically.
These endpoints follow the standard pattern:
/api/lang/word/...
"""

from flask import Blueprint, jsonify, send_file, abort
from utils.word_utils import get_word_preview
import urllib.parse

# Create a blueprint with standardized prefix
wordform_api_bp = Blueprint("wordform_api", __name__, url_prefix="/api/lang/word")


@wordform_api_bp.route("/<target_language_code>/<word>/preview")
def word_preview(target_language_code: str, word: str):
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
def get_mp3(target_language_code: str, word: str):
    """Return the MP3 file for the given word."""
    mp3_filen = f"{word}.mp3"
    try:
        return send_file(mp3_filen, mimetype="audio/mpeg")
    except FileNotFoundError:
        abort(404, description="MP3 file not found")
