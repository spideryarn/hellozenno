from flask import (
    Blueprint,
    render_template,
    request,
)
import logging
import urllib.parse

from utils.flask_view_utils import redirect_to_view
from utils.lang_utils import get_language_name
from views.wordform_views import get_wordform_metadata_vw, wordform_views_bp


search_views_bp = Blueprint("search", __name__, url_prefix="/lang")

# Configure logging
logger = logging.getLogger(__name__)


@search_views_bp.route("/<target_language_code>/search")
def search_landing_vw(target_language_code: str):
    """Landing page for word search with a search form."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    if query:
        # Fix URL encoding issues with Vercel by explicitly unquoting the query parameter
        query = urllib.parse.unquote(query)

        # If there's a query, redirect to the search endpoint
        return redirect_to_view(
            search_views_bp,
            search_word_vw,
            target_language_code=target_language_code,
            wordform=query,
        )

    return render_template(
        "search.jinja",
        target_language_code=target_language_code,
        target_language_name=get_language_name(target_language_code),
    )


@search_views_bp.route("/<target_language_code>/search/<wordform>")
def search_word_vw(target_language_code: str, wordform: str):
    """
    Search for a word and redirect to the wordform view.
    Currently just redirects to the wordform view, but can be enhanced in the future
    to support more sophisticated search functionality.
    """
    # Fix URL encoding issues with Vercel by explicitly unquoting the wordform parameter
    wordform = urllib.parse.unquote(wordform)

    return redirect_to_view(
        wordform_views_bp,
        get_wordform_metadata_vw,
        target_language_code=target_language_code,
        wordform=wordform,
    )
