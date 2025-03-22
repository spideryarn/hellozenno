from db_models import Sentence, Sourcedir, Sourcefile, SourcefileWordform
from utils.audio_utils import ensure_model_audio_data
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_random_sentence
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas
from views.flashcard_views import flashcard_views_bp


from flask import jsonify, request, url_for
from peewee import DoesNotExist


@flashcard_views_bp.route(
    "/<language_code>/flashcards/api/sentence/<slug>", methods=["GET"]
)
def flashcard_sentence_api(language_code: str, slug: str):
    """JSON API endpoint for a specific sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
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

    # Get parameters from query
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Prepare response data
    response_data = {
        "id": sentence.id,
        "slug": sentence.slug,
        "text": sentence.sentence,
        "translation": sentence.translation,
        "lemma_words": sentence.lemma_words,
        "audio_url": url_for(
            "sentence_views.get_sentence_audio",
            language_code=language_code,
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


@flashcard_views_bp.route("/<language_code>/flashcards/api/random", methods=["GET"])
def random_flashcard_api(language_code: str):
    """JSON API endpoint for a random sentence."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    lemmas = None

    # If sourcedir is provided, get lemmas for filtering
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(language_code, sourcedir_slug)
        except DoesNotExist:
            return jsonify({"error": "Sourcedir not found"}), 404
    # If sourcefile is provided, get its lemmas for filtering
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(
                language_code, sourcefile_entry.sourcedir.slug, sourcefile_slug
            )
        except DoesNotExist:
            return jsonify({"error": "Sourcefile not found"}), 404

    # Get random sentence
    sentence_data = get_random_sentence(
        target_language_code=language_code, required_lemmas=lemmas if lemmas else None
    )

    if not sentence_data:
        return jsonify({"error": "No matching sentences found"}), 404

    # Get the full sentence object
    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code)
            & (Sentence.id == sentence_data["id"])
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
            "sentence_views.get_sentence_audio",
            language_code=language_code,
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
