from flask import Blueprint, abort, jsonify, redirect, url_for, send_file
from peewee import DoesNotExist

from utils.flask_view_utils import full_url_for
from utils.word_utils import get_word_preview
from db_models import Lemma

# Create a Blueprint for our API routes
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/")
def home():
    return redirect(url_for("api.urls"))


@api_bp.route("/urls")
def urls():
    urls = {
        "word preview": full_url_for(
            "api.word_preview", target_language_code="el", word="καλός"
        ),
    }
    return jsonify(urls)


@api_bp.route("/word-preview/<target_language_code>/<word>")
def word_preview(target_language_code: str, word: str):
    """Get preview data for word tooltips."""
    preview = get_word_preview(target_language_code, word)
    if preview is None:
        response = jsonify(
            {"error": "Not Found", "description": f"Word '{word}' not found"}
        )
        response.status_code = 404
        return response
    response = jsonify(preview)
    response.headers["Cache-Control"] = "public, max-age=60"  # Cache for 1 minute
    return response


@api_bp.route("/<lang_code>/words/<word>/mp3")
def get_mp3(lang_code: str, word: str):
    """Return the MP3 file for the given word."""
    mp3_filen = f"{word}.mp3"
    try:
        return send_file(mp3_filen, mimetype="audio/mpeg")
    except FileNotFoundError:
        abort(404, description="MP3 file not found")


@api_bp.route("/<language_code>/lemma/<lemma>/data")
def get_lemma_data(language_code: str, lemma: str):
    """Get detailed data for a specific lemma."""
    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma) & (Lemma.language_code == language_code)
        )
        data = lemma_model.to_dict()
        return jsonify(data)
    except DoesNotExist:
        response = jsonify(
            {"error": "Not Found", "description": f"Lemma '{lemma}' not found"}
        )
        response.status_code = 404
        return response
