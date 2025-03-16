from flask import (
    Blueprint,
    render_template,
    send_from_directory,
)
import logging
import os

from utils.flask_view_utils import redirect_to_view
from utils.lang_utils import get_all_languages


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


@views_bp.route("/favicon.ico", defaults={"trailing_slash": ""})
@views_bp.route("/favicon.ico/", defaults={"trailing_slash": "/"})
def favicon(trailing_slash):
    """Handle favicon.ico requests with or without trailing slash."""
    return send_from_directory(
        os.path.join(os.path.dirname(views_bp.root_path), "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
