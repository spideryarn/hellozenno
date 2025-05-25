from db_models import Sentence, Sourcedir, Sourcefile, SourcefileWordform, Wordform
from utils.audio_utils import ensure_model_audio_data
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_random_sentence
from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas, normalize_text
from utils.vocab_llm_utils import extract_tokens, create_interactive_word_data
from utils.flashcard_utils import (
    get_flashcard_landing_data,
    get_flashcard_sentence_data,
    get_random_flashcard_data,
)
from views.flashcard_views import flashcard_views_bp

# Import auth decorator
from utils.auth_utils import api_auth_optional

from flask import jsonify, request, url_for, Blueprint
from peewee import DoesNotExist

# Create a separate blueprint for API endpoints
flashcard_api_bp = Blueprint("flashcard_api", __name__, url_prefix="/api/lang")


@flashcard_api_bp.route(
    "/<target_language_code>/flashcards/sentence/<slug>", methods=["GET"]
)
@api_auth_optional  # Auth is optional here
def flashcard_sentence_api(target_language_code: str, slug: str):
    """JSON API endpoint for a specific sentence."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_sentence_data(
        target_language_code=target_language_code,
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


@flashcard_api_bp.route("/<target_language_code>/flashcards/random", methods=["GET"])
@api_auth_optional  # Auth is optional here
def random_flashcard_api(target_language_code: str):
    """JSON API endpoint for a random sentence."""
    from loguru import logger

    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    logger.info(
        f"Fetching random flashcard: language={target_language_code}, sourcefile={sourcefile_slug}, sourcedir={sourcedir_slug}"
    )

    # Get profile from flask g object if available
    profile = None
    from flask import g

    if hasattr(g, "profile") and g.profile:
        profile = g.profile

    # Use the shared utility function
    data = get_random_flashcard_data(
        target_language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
        profile=profile,
    )

    # Handle error responses with proper status codes
    if "error" in data:
        status_code = data.get("status_code", 404)
        # Log the error with appropriate level based on status code
        if status_code >= 500:
            logger.error(f"Error getting random flashcard: {data['error']}")
        elif status_code == 204:
            logger.info(f"No matching sentences found: {data['error']}")
        else:
            logger.warning(f"Issue getting random flashcard: {data['error']}")

        return jsonify({"error": data["error"]}), status_code

    # Get the full sentence object to include more information
    try:
        sentence = Sentence.get(
            (Sentence.target_language_code == target_language_code)
            & (Sentence.id == data["id"])  # type: ignore
        )
    except DoesNotExist:
        logger.error(
            f"Sentence not found with ID {data['id']} for language {target_language_code}"
        )
        return jsonify({"error": "Sentence not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting random flashcard: {str(e)}")
        return jsonify({"error": "Error getting random flashcard"}), 500

    # Pre-generate audio if needed
    if not sentence.audio_data:
        try:
            ensure_model_audio_data(
                model=sentence,
                should_add_delays=True,
                verbose=1,
            )
        except Exception as e:
            # Log error properly but continue - audio can be generated on demand
            logger.error(f"Error pre-generating audio: {str(e)}")

    # Add word recognition data for enhanced text tooltips
    recognized_words = []
    try:
        # Extract tokens from the sentence text
        tokens_in_text = extract_tokens(str(sentence.sentence))

        # Query database for all wordforms in this language that might be in the text
        wordforms = list(
            Wordform.select().where(
                (Wordform.target_language_code == target_language_code)
            )
        )

        # Filter wordforms in Python using normalize_text to match tokens
        normalized_tokens = {normalize_text(t) for t in tokens_in_text}
        matching_wordforms = [
            wf for wf in wordforms if normalize_text(wf.wordform) in normalized_tokens
        ]

        # Convert to dictionary format for create_interactive_word_data
        wordforms_d = []
        for wordform in matching_wordforms:
            wordform_d = wordform.to_dict()
            wordforms_d.append(wordform_d)

        # Create structured word recognition data
        recognized_words, found_wordforms = create_interactive_word_data(
            text=str(sentence.sentence),
            wordforms=wordforms_d,
            target_language_code=target_language_code,
        )
    except Exception as e:
        # Log error but don't fail the entire request
        logger.error(
            f"Error generating word recognition data for sentence {sentence.id}: {e}"
        )
        recognized_words = []

    # Prepare response data
    response_data = {
        "id": sentence.id,
        "slug": sentence.slug,
        "text": sentence.sentence,
        "translation": sentence.translation,
        "lemma_words": sentence.lemma_words,
        "recognized_words": recognized_words,  # Add word recognition data
        "audio_url": url_for(
            "sentence_api.get_sentence_audio_api",
            target_language_code=target_language_code,
            sentence_id=sentence.id,
        ),
        "metadata": {
            "target_language_code": target_language_code,
            "language_name": get_language_name(target_language_code),
        },
    }

    # Add source information if present
    if sourcefile_slug:
        response_data["metadata"]["sourcefile"] = sourcefile_slug
    if sourcedir_slug:
        response_data["metadata"]["sourcedir"] = sourcedir_slug

    logger.info(
        f"Successfully retrieved random flashcard with sentence ID {sentence.id}"
    )
    return jsonify(response_data)


@flashcard_api_bp.route("/<target_language_code>/flashcards/landing", methods=["GET"])
def flashcard_landing_api(target_language_code: str):
    """JSON API endpoint for the flashcard landing page."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    # Use the shared utility function
    data = get_flashcard_landing_data(
        target_language_code=target_language_code,
        sourcefile_slug=sourcefile_slug,
        sourcedir_slug=sourcedir_slug,
    )

    if "error" in data:
        return jsonify({"error": data["error"]}), 404

    return jsonify(data)
