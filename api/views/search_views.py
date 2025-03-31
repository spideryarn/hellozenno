from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
)
import logging

from utils.search_utils import prepare_search_landing_data, get_wordform_redirect_url

search_views_bp = Blueprint("search_views", __name__, url_prefix="/language")

# Configure logging
logger = logging.getLogger(__name__)


@search_views_bp.route("/<target_language_code>/search")
def search_landing_vw(target_language_code: str):
    """Landing page for word search with a search form."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    # Prepare data using shared utility function
    data = prepare_search_landing_data(target_language_code, query)

    if data.get("has_query"):
        # If there's a query, redirect to the search endpoint
        redirect_url, _ = get_wordform_redirect_url(target_language_code, data["query"])
        return redirect(redirect_url)

    return render_template(
        "search.jinja",
        target_language_code=target_language_code,
        target_language_name=data["target_language_name"],
    )


@search_views_bp.route("/<target_language_code>/search/<wordform>")
def search_word_vw(target_language_code: str, wordform: str):
    """
    Search for a word and redirect to the wordform view.
    Currently just redirects to the wordform view, but can be enhanced in the future
    to support more sophisticated search functionality.
    """
    # Get redirect URL using shared utility function
    redirect_url, _ = get_wordform_redirect_url(target_language_code, wordform)
    return redirect(redirect_url)
