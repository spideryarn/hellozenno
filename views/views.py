from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
)
import logging
import os

from utils.flask_view_utils import redirect_to_view

from utils.lang_utils import get_all_languages, get_language_name
from views.wordform_views import get_wordform_metadata, wordform_views_bp


views_bp = Blueprint("views", __name__)

# Configure logging
logger = logging.getLogger(__name__)


@views_bp.route("/")
def home():
    return redirect_to_view(views_bp, languages)


@views_bp.route("/languages")
def languages():
    supported_languages = get_all_languages()
    return render_template(
        "languages.jinja",
        languages=supported_languages,
    )


@views_bp.route("/experim")
def experim():
    """A simple experimental page that returns hello world."""
    # Sample lemma data for testing the MiniLemma component
    sample_lemmas = [
        {
            "lemma": "γράφω",
            "partOfSpeech": "verb",
            "translations": ["to write", "to draw", "to record"],
            "href": "/el/lemma/γράφω",
        },
        {
            "lemma": "πόλη",
            "partOfSpeech": "noun",
            "translations": ["city", "town"],
            "href": "/el/lemma/πόλη",
        },
        {
            "lemma": "καλός",
            "partOfSpeech": "adjective",
            "translations": ["good", "beautiful", "fine"],
            "href": "/el/lemma/καλός",
        },
    ]

    return render_template(
        "experim.jinja",
        sample_lemmas=sample_lemmas,
    )


@views_bp.route("/<target_language_code>/search")
def search_landing(target_language_code: str):
    """Landing page for word search with a search form."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    if query:
        # Fix URL encoding issues with Vercel by explicitly unquoting the query parameter
        import urllib.parse
        query = urllib.parse.unquote(query)
        
        # If there's a query, redirect to the search endpoint
        return redirect_to_view(
            views_bp,
            search_word,
            target_language_code=target_language_code,
            wordform=query,
        )

    return render_template(
        "search.jinja",
        target_language_code=target_language_code,
        target_language_name=get_language_name(target_language_code),
    )


@views_bp.route("/<target_language_code>/search/<wordform>")
def search_word(target_language_code: str, wordform: str):
    """
    Search for a word and redirect to the wordform view.
    Currently just redirects to the wordform view, but can be enhanced in the future
    to support more sophisticated search functionality.
    """
    # Fix URL encoding issues with Vercel by explicitly unquoting the wordform parameter
    import urllib.parse
    wordform = urllib.parse.unquote(wordform)
    
    return redirect_to_view(
        wordform_views_bp,
        get_wordform_metadata,
        target_language_code=target_language_code,
        wordform=wordform,
    )


@views_bp.route("/favicon.ico", defaults={"trailing_slash": ""})
@views_bp.route("/favicon.ico/", defaults={"trailing_slash": "/"})
def favicon(trailing_slash):
    """Handle favicon.ico requests with or without trailing slash."""
    return send_from_directory(
        os.path.join(os.path.dirname(views_bp.root_path), "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
