import urllib.parse
from flask import url_for
import logging

from utils.lang_utils import get_language_name
from utils.url_registry import endpoint_for

# Configure logging
logger = logging.getLogger(__name__)


def prepare_search_landing_data(target_language_code: str, query: str = ""):
    """
    Prepare data for search landing page.

    Args:
        target_language_code: The target language code
        query: The search query, if any

    Returns:
        dict: Data for the search landing page
    """
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

    return response_data


def get_wordform_redirect_url(target_language_code: str, wordform: str):
    """
    Get the URL to redirect to for a wordform search.

    Args:
        target_language_code: The target language code
        wordform: The wordform to search for

    Returns:
        str: The URL to redirect to
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

    return redirect_url, wordform
