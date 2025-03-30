from flask import (
    Blueprint,
    request,
    jsonify,
    url_for,
)
import logging
import urllib.parse

from utils.lang_utils import get_language_name
from utils.url_registry import endpoint_for

# Configure logging
logger = logging.getLogger(__name__)

search_api_bp = Blueprint("search_api", __name__, url_prefix="/api/lang")


@search_api_bp.route("/<target_language_code>/search")
def search_landing_api(target_language_code: str):
    """API endpoint for search landing page data."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    response_data = {
        "target_language_code": target_language_code,
        "target_language_name": get_language_name(target_language_code),
    }

    if query:
        # Fix URL encoding issues with Vercel by explicitly unquoting the query parameter
        query = urllib.parse.unquote(query)

        # If there's a query, include it in the response data
        response_data["query"] = query
        response_data["has_query"] = True
    else:
        response_data["has_query"] = False

    return jsonify(response_data)


@search_api_bp.route("/<target_language_code>/search/<wordform>")
def search_word_api(target_language_code: str, wordform: str):
    """
    API endpoint for searching a word.
    Returns the appropriate URL to redirect to (wordform view).
    """
    # Fix URL encoding issues with Vercel by explicitly unquoting the wordform parameter
    wordform = urllib.parse.unquote(wordform)

    # Import here to avoid circular dependencies
    from views.wordform_views import get_wordform_metadata_vw

    # Get the URL to redirect to
    redirect_url = url_for(
        endpoint_for(get_wordform_metadata_vw),
        target_language_code=target_language_code,
        wordform=wordform,
    )

    return jsonify(
        {
            "target_language_code": target_language_code,
            "wordform": wordform,
            "redirect_url": redirect_url,
        }
    )
