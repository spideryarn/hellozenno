from flask import (
    Blueprint,
    render_template,
    send_from_directory,
)
import logging
import os

from utils.flask_view_utils import redirect_to_view
from utils.lang_utils import get_all_languages


core_views_bp = Blueprint("core_views", __name__)

# Configure logging
logger = logging.getLogger(__name__)


@core_views_bp.route("/")
def home_vw():
    return redirect_to_view(core_views_bp, languages_list_vw)


@core_views_bp.route("/lang")
def languages_list_vw(trailing_slash=""):
    """Display all supported languages."""
    # Import here to avoid circular imports
    from views.sourcedir_views import sourcedirs_for_language_vw

    languages = get_all_languages()
    return render_template(
        "languages.jinja",
        languages=languages,
    )


@core_views_bp.route("/experim")
def experim_vw():
    """A simple experimental page that returns hello world."""
    # Sample lemma data for testing the MiniLemma component
    sample_lemmas = [
        {
            "lemma": "γράφω",
            "partOfSpeech": "verb",
            "translations": ["to write", "to draw", "to record"],
            "href": "/lang/el/lemma/γράφω",
        },
        {
            "lemma": "πόλη",
            "partOfSpeech": "noun",
            "translations": ["city", "town"],
            "href": "/lang/el/lemma/πόλη",
        },
        {
            "lemma": "καλός",
            "partOfSpeech": "adjective",
            "translations": ["good", "beautiful", "fine"],
            "href": "/lang/el/lemma/καλός",
        },
    ]

    return render_template(
        "experim.jinja",
        sample_lemmas=sample_lemmas,
    )


@core_views_bp.route("/favicon.ico", defaults={"trailing_slash": ""})
@core_views_bp.route("/favicon.ico/", defaults={"trailing_slash": "/"})
def favicon_vw(trailing_slash):
    """Handle favicon.ico requests with or without trailing slash."""
    return send_from_directory(
        os.path.join(os.path.dirname(core_views_bp.root_path), "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
