"""Core API endpoints.

Contains the base API routes and documentation.
"""

from flask import Blueprint, jsonify, redirect, url_for
from utils.flask_view_utils import full_url_for

# Create the core API blueprint
core_api_bp = Blueprint("core_api", __name__, url_prefix="/api")


@core_api_bp.route("/")
def home():
    """API home page."""
    return redirect(url_for("core_api.urls"))


@core_api_bp.route("/urls")
def urls():
    """List available API URLs and examples."""
    urls = {
        "word_preview": full_url_for(
            "wordform_api.word_preview", target_language_code="el", word="καλός"
        ),
        "phrase_preview": full_url_for(
            "phrase_api.phrase_preview", target_language_code="el", phrase="καλημέρα σας"
        ),
        "lemma_data": full_url_for(
            "lemma_api.get_lemma_data", target_language_code="el", lemma="καλός"
        ),
        "word_mp3": full_url_for(
            "wordform_api.get_mp3", target_language_code="el", word="καλός"
        )
    }
    return jsonify(urls)