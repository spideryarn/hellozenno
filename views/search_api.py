from flask import (
    Blueprint,
    request,
    jsonify,
)
import logging

from utils.search_utils import prepare_search_landing_data, get_wordform_redirect_url

# Configure logging
logger = logging.getLogger(__name__)

search_api_bp = Blueprint("search_api", __name__, url_prefix="/api/lang")


@search_api_bp.route("/<target_language_code>/search")
def search_landing_api(target_language_code: str):
    """API endpoint for search landing page data."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    # Prepare data using shared utility function
    response_data = prepare_search_landing_data(target_language_code, query)
    return jsonify(response_data)


@search_api_bp.route("/<target_language_code>/search/<wordform>")
def search_word_api(target_language_code: str, wordform: str):
    """
    API endpoint for searching a word.
    Returns the appropriate URL to redirect to (wordform view).
    """
    # Get redirect URL using shared utility function
    redirect_url, decoded_wordform = get_wordform_redirect_url(
        target_language_code, wordform
    )

    return jsonify(
        {
            "target_language_code": target_language_code,
            "wordform": decoded_wordform,
            "redirect_url": redirect_url,
        }
    )
