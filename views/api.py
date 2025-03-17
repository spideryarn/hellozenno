from flask import Blueprint, abort, jsonify, redirect, url_for, send_file, request
from peewee import DoesNotExist

from utils.flask_view_utils import full_url_for
from utils.word_utils import get_word_preview
from db_models import Lemma, Phrase
import views.sourcefile_views as sourcefile_views

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
        "phrase preview": full_url_for(
            "api.phrase_preview", target_language_code="el", phrase="καλημέρα σας"
        ),
    }
    return jsonify(urls)


@api_bp.route("/lang/<target_language_code>/word-preview/<word>")
def word_preview(target_language_code: str, word: str):
    """Get preview data for word tooltips."""
    # Fix URL encoding issues with Vercel by explicitly unquoting the word parameter
    import urllib.parse
    word = urllib.parse.unquote(word)
    
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


@api_bp.route("/lang/<target_language_code>/phrase-preview/<phrase>")
def phrase_preview(target_language_code: str, phrase: str):
    """Get preview data for phrase tooltips."""
    # Fix URL encoding issues with Vercel by explicitly unquoting the phrase parameter
    import urllib.parse
    phrase = urllib.parse.unquote(phrase)
    
    try:
        # Try to find the phrase in the database
        phrase_model = Phrase.select().where(
            (Phrase.canonical_form == phrase) & 
            (Phrase.language_code == target_language_code)
        ).first()
        
        if phrase_model is None:
            # Try to find it by a raw form
            for p in Phrase.select().where(Phrase.language_code == target_language_code):
                if phrase in p.raw_forms:
                    phrase_model = p
                    break
        
        if phrase_model is None:
            response = jsonify(
                {"error": "Not Found", "description": f"Phrase '{phrase}' not found"}
            )
            response.status_code = 404
            return response
        
        # Create preview data
        preview = {
            "canonical_form": phrase_model.canonical_form,
            "translations": phrase_model.translations,
            "part_of_speech": phrase_model.part_of_speech,
            "usage_notes": phrase_model.usage_notes,
            "difficulty_level": phrase_model.difficulty_level,
            "register": phrase_model.register,
        }
        
        response = jsonify(preview)
        response.headers["Cache-Control"] = "public, max-age=60"  # Cache for 1 minute
        return response
    except Exception as e:
        response = jsonify(
            {"error": "Internal Server Error", "description": str(e)}
        )
        response.status_code = 500
        return response


@api_bp.route("/lang/<target_language_code>/sourcefile/<sourcedir_slug>/<sourcefile_slug>/process_individual", methods=["POST"])
def process_individual_words_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Process individual words of a sourcefile."""
    try:
        sourcefile_views.process_individual_words(target_language_code, sourcedir_slug, sourcefile_slug)
        return jsonify({"success": True})
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response
