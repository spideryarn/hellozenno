from db_models import Sentence, Sourcedir, Sourcefile, SourcefileWordform
from utils.audio_utils import ensure_model_audio_data
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_random_sentence
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas
from utils.flashcard_utils import (
    get_flashcard_landing_data,
    get_flashcard_sentence_data,
    get_random_flashcard_data,
)
from views.flashcard_views import flashcard_views_bp


from flask import jsonify, request, url_for, Blueprint
from peewee import DoesNotExist

# Create a separate blueprint for API endpoints
flashcard_api_bp = Blueprint("flashcard_api", __name__, url_prefix="/api/lang")


@flashcard_api_bp.route("/<language_code>/flashcards/sentence/<slug>", methods=["GET"])
def flashcard_sentence_api(language_code: str, slug: str):
    """JSON API endpoint for a specific sentence."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_sentence_data(
        language_code=language_code,
        slug=slug,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        return jsonify({"error": data["error"]}), 404

    # Remove the sentence model from the API response
    if "sentence" in data:
        del data["sentence"]

    return jsonify(data)


@flashcard_api_bp.route("/<language_code>/flashcards/random", methods=["GET"])
def random_flashcard_api(language_code: str):
    """JSON API endpoint for a random sentence."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_random_flashcard_data(
        language_code=language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        return jsonify({"error": data["error"]}), 404

    # Get the full sentence object to include more information
    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code)
            & (Sentence.id == data["id"])  # type: ignore
        )
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404

    # Pre-generate audio if needed
    if not sentence.audio_data:
        try:
            ensure_model_audio_data(
                model=sentence,
                should_add_delays=True,
                verbose=1,
            )
        except Exception as e:
            # Log error but continue - audio can be generated on demand
            print(f"Error pre-generating audio: {e}")

    # Prepare response data
    response_data = {
        "id": sentence.id,
        "slug": sentence.slug,
        "text": sentence.sentence,
        "translation": sentence.translation,
        "lemma_words": sentence.lemma_words,
        "audio_url": url_for(
            "sentence_api.get_sentence_audio_api",
            target_language_code=language_code,
            sentence_id=sentence.id,
        ),
        "metadata": {
            "language_code": language_code,
            "language_name": get_language_name(language_code),
        },
    }

    # Add source information if present
    if sourcefile_slug:
        response_data["metadata"]["sourcefile"] = sourcefile_slug
    if sourcedir_slug:
        response_data["metadata"]["sourcedir"] = sourcedir_slug

    return jsonify(response_data)


@flashcard_api_bp.route("/<language_code>/flashcards/landing", methods=["GET"])
def flashcard_landing_api(language_code: str):
    """JSON API endpoint for the flashcard landing page."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_landing_data(
        language_code=language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        return jsonify({"error": data["error"]}), 404

    return jsonify(data)
