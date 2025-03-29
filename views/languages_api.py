"""API endpoints for languages.

All endpoints for interacting with languages programmatically.
These endpoints follow the standard pattern:
/api/lang/...
"""

from flask import Blueprint, jsonify, request
import logging

from utils.lang_utils import get_all_languages, get_language_name


logger = logging.getLogger(__name__)

languages_api_bp = Blueprint("languages_api", __name__, url_prefix="/api/lang")


@languages_api_bp.route("/languages", methods=["GET"])
def get_languages_api():
    """Get a list of all supported languages.

    Returns:
        JSON response with language data
    """
    languages = get_all_languages()
    return jsonify(languages)


@languages_api_bp.route("/language_name/<language_code>", methods=["GET"])
def get_language_name_api(language_code):
    """Get the display name for a language code.

    Args:
        language_code: 2-letter language code

    Returns:
        JSON response with the language name
    """
    try:
        name = get_language_name(language_code)
        return jsonify({"code": language_code, "name": name})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
