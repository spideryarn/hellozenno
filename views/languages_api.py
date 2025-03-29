"""API endpoints for languages.

All endpoints for interacting with languages programmatically.
These endpoints follow the standard pattern:
/api/lang/...
"""

from flask import Blueprint, jsonify
import logging

from utils.lang_utils import get_all_languages


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
