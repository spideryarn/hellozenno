from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    send_from_directory,
)
import logging
import os

from utils.url_registry import endpoint_for
from views.languages_views import languages_list_vw


core_views_bp = Blueprint("core_views", __name__)

# Configure logging
logger = logging.getLogger(__name__)


@core_views_bp.route("/")
def home_vw():
    return redirect(url_for(endpoint_for(languages_list_vw)))


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


@core_views_bp.route("/favicon.ico")
def favicon_vw():
    """Serve the site's favicon.

    We explicitly serve the favicon from the backend static directory to ensure
    it works consistently in tests and production.
    """
    static_img_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../static/img"
    )
    return send_from_directory(static_img_dir, "favicon.ico")
