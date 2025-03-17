"""API endpoints for sentences.

All endpoints for interacting with sentences programmatically.
These endpoints follow the standard pattern:
/api/lang/sentence/...
"""

from flask import Blueprint, jsonify, request, send_file
import io
from peewee import DoesNotExist

from db_models import Sentence
from utils.sentence_utils import get_random_sentence
from utils.audio_utils import ensure_model_audio_data

# Create a blueprint with standardized prefix
sentence_api_bp = Blueprint("sentence_api", __name__, url_prefix="/api/lang/sentence")


@sentence_api_bp.route("/<target_language_code>/random", methods=["GET"])
def get_random_sentence_api(target_language_code: str):
    """Get a random sentence for the given language.

    Supports filtering by lemmas via the lemmas[] query parameter.
    Returns 404 if no matching sentences are found.
    """
    # Get lemmas from query params if provided
    lemmas = request.args.getlist("lemmas[]")

    # Get random sentence
    sentence = get_random_sentence(
        target_language_code=target_language_code, required_lemmas=lemmas if lemmas else None
    )

    if not sentence:
        return jsonify({"error": "No matching sentences found"}), 404

    return jsonify(sentence)


@sentence_api_bp.route("/<target_language_code>/<int:sentence_id>/audio", methods=["GET"])
def get_sentence_audio_api(target_language_code: str, sentence_id: int):
    """Serve audio data for a sentence from the database.

    Args:
        target_language_code: ISO language code
        sentence_id: Database ID of the sentence

    Returns:
        Audio file response or 404 if not found
    """
    try:
        sentence = Sentence.get(
            (Sentence.id == sentence_id) & (Sentence.language_code == target_language_code)  # type: ignore
        )
        if not sentence.audio_data:
            return jsonify({"error": "Audio not found"}), 404

        return send_file(
            io.BytesIO(sentence.audio_data),
            mimetype="audio/mpeg",
            as_attachment=False,
        )
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_api_bp.route("/<target_language_code>/<slug>", methods=["DELETE"])
def delete_sentence_api(target_language_code: str, slug: str):
    """Delete a sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.language_code == target_language_code) & (Sentence.slug == slug)
        )
        sentence.delete_instance()
        return "", 204
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_api_bp.route("/<target_language_code>/<slug>/rename", methods=["PUT"])
def rename_sentence_api(target_language_code: str, slug: str):
    """Rename/edit a sentence."""
    try:
        data = request.get_json()
        if not data or "new_text" not in data:
            return jsonify({"error": "Missing new_text parameter"}), 400

        new_text = data["new_text"].strip()
        if not new_text:
            return jsonify({"error": "Invalid sentence text"}), 400

        sentence = Sentence.get(
            (Sentence.language_code == target_language_code) & (Sentence.slug == slug)
        )

        # Update the sentence text - this will trigger slug regeneration in save()
        sentence.sentence = new_text
        sentence.slug = slugify(new_text)  # Manually update slug
        sentence.save()

        return jsonify({"new_text": new_text, "new_slug": sentence.slug}), 200

    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404
    except NameError:
        # Import slugify here since it might not be available at module level
        from slugify import slugify
        # Try again with the import
        sentence = Sentence.get(
            (Sentence.language_code == target_language_code) & (Sentence.slug == slug)
        )
        sentence.sentence = new_text
        sentence.slug = slugify(new_text)
        sentence.save()
        return jsonify({"new_text": new_text, "new_slug": sentence.slug}), 200


@sentence_api_bp.route("/<target_language_code>/<slug>/generate_audio", methods=["POST"])
def generate_sentence_audio_api(target_language_code: str, slug: str):
    """Generate audio for a sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.language_code == target_language_code) & (Sentence.slug == slug)
        )

        if not sentence.sentence:
            return (
                jsonify({"error": "No text content available for audio generation"}),
                400,
            )

        # Generate audio data
        ensure_model_audio_data(sentence, should_add_delays=True, verbose=1)

        return "", 204

    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to generate audio: {str(e)}"}), 500