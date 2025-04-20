from flask import (
    Blueprint,
    request,
    jsonify,
)
import logging
import urllib.parse

from utils.search_utils import prepare_search_landing_data, get_wordform_redirect_url
from utils.word_utils import find_or_create_wordform
from utils.lang_utils import get_language_name

# Import auth decorator and exception
from utils.auth_utils import api_auth_optional
from utils.exceptions import AuthenticationRequiredForGenerationError

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


@search_api_bp.route("/<target_language_code>/unified_search")
@api_auth_optional  # Auth is needed if wordform generation is triggered
def unified_search_api(target_language_code: str):
    """
    Unified search endpoint that handles all search cases in one response.
    Returns a consistent JSON structure regardless of search outcome.

    This endpoint replaces the traditional redirect-based search flow with a
    single API that returns all search results data, allowing the client to
    handle presentation decisions.

    Status values:
    - empty_query: No search term provided
    - found: Exact wordform match found
    - multiple_matches: Multiple potential matches found
    - redirect: Single match found, but needs redirection (usually to create the wordform)
    - invalid: No matches found

    Query params:
    - q: The search query text
    """
    # Get the search query from URL parameters
    query = request.args.get("q", "")

    # Handle empty query case
    if not query:
        return jsonify(
            {
                "status": "empty_query",
                "query": "",
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
                "data": {},
            }
        )

    # Normalize query (handle URL encoding)
    query = urllib.parse.unquote(query)

    try:
        # Use the existing find_or_create_wordform function
        # This handles all the complex search logic and fallbacks
        # It may raise AuthenticationRequiredForGenerationError
        result = find_or_create_wordform(target_language_code, query)

        # Build a consistent response structure
        response = {
            "status": result["status"],
            "query": query,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "data": result["data"],
        }

        return jsonify(response)
    except AuthenticationRequiredForGenerationError:
        # Handle the case where generation requires login
        error_response = {
            "status": "authentication_required",
            "query": query,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "error": "Authentication required to search for or generate wordform details",
            "authentication_required_for_generation": True,
            "data": {},
        }
        return jsonify(error_response), 401
    except Exception as e:
        # Log and return a clear error message
        logger.exception(f"Error in unified search: {e}")

        # Return error with status code 500
        error_response = {
            "status": "error",
            "query": query,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "error": str(e),
            "data": {},
        }
        return jsonify(error_response), 500
