"""API endpoints for sentences.

All endpoints for interacting with sentences programmatically.
These endpoints follow the standard pattern:
/api/lang/sentence/...
"""

from flask import Blueprint, jsonify, request, send_file
import io
from peewee import DoesNotExist
from slugify import slugify

from db_models import Sentence, SentenceAudio
from utils.sentence_utils import (
    get_random_sentence,
    get_detailed_sentence_data,
    get_all_sentences,
)
from utils.audio_utils import ensure_sentence_audio_variants, stream_random_sentence_audio
from utils.exceptions import AuthenticationRequiredForGenerationError
from utils.auth_utils import api_auth_required

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
        target_language_code=target_language_code,
        required_lemmas=lemmas if lemmas else None,
    )

    if not sentence:
        return jsonify({"error": "No matching sentences found"}), 404

    return jsonify(sentence)


@sentence_api_bp.route("/<target_language_code>/<slug>", methods=["GET"])
def get_sentence_by_slug_api(target_language_code: str, slug: str):
    """Get a specific sentence by its slug.

    Returns detailed information about the sentence, including:
    - Sentence text and translation
    - Metadata (created/updated timestamps)
    - Enhanced text with interactive word links
    - Associated lemmas
    """
    try:
        # Use the shared utility function to get sentence data
        sentence_data = get_detailed_sentence_data(target_language_code, slug)
        return jsonify(sentence_data)
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_api_bp.route(
    "/<target_language_code>/<int:sentence_id>/audio", methods=["GET"]
)
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
            (Sentence.id == sentence_id) & (Sentence.target_language_code == target_language_code)  # type: ignore
        )
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404

    variant_id_param = request.args.get("variant_id")
    variant = None

    if variant_id_param:
        try:
            variant = SentenceAudio.get(
                (SentenceAudio.id == int(variant_id_param))
                & (SentenceAudio.sentence == sentence)
            )
        except (DoesNotExist, ValueError):
            return jsonify({"error": "Audio not found"}), 404
    else:
        variant = stream_random_sentence_audio(sentence.id)
    if variant is None:
        return jsonify({"error": "Audio not found"}), 404

    response = send_file(
        io.BytesIO(variant.audio_data),
        mimetype="audio/mpeg",
        as_attachment=False,
    )
    metadata = variant.metadata or {}
    voice_name = metadata.get("voice_name")
    if voice_name:
        response.headers["X-Voice-Name"] = voice_name
    response.headers["X-Voice-Variant-Id"] = str(variant.id)
    response.headers["X-Audio-Provider"] = variant.provider
    return response


@sentence_api_bp.route(
    "/<target_language_code>/<int:sentence_id>/audio/variants", methods=["GET"]
)
def get_sentence_audio_variants_api(target_language_code: str, sentence_id: int):
    """List audio variants for a sentence."""

    try:
        sentence = Sentence.get(
            (Sentence.id == sentence_id)
            & (Sentence.target_language_code == target_language_code)
        )
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404

    variants = (
        SentenceAudio.select()
        .where(SentenceAudio.sentence == sentence)
        .order_by(SentenceAudio.created_at)
    )
    payload = []
    for variant in variants:
        metadata = variant.metadata or {}
        payload.append(
            {
                "id": variant.id,
                "provider": variant.provider,
                "metadata": metadata,
                "created_at": (
                    variant.created_at.isoformat()
                    if getattr(variant, "created_at", None)
                    else None
                ),
                "url": f"/api/lang/sentence/{target_language_code}/{sentence_id}/audio?variant_id={variant.id}",
            }
        )

    return jsonify(payload)


# For compatibility with SvelteKit, add a route with 'language' in the path for audio too
@sentence_api_bp.route(
    "/language/<target_language_code>/<int:sentence_id>/audio", methods=["GET"]
)
def get_sentence_audio_by_language_api(target_language_code: str, sentence_id: int):
    """Alias for get_sentence_audio_api for compatibility with SvelteKit."""
    return get_sentence_audio_api(target_language_code, sentence_id)


@sentence_api_bp.route("/<target_language_code>/<slug>", methods=["DELETE"])
@api_auth_required
def delete_sentence_api(target_language_code: str, slug: str):
    """Delete a sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.target_language_code == target_language_code)
            & (Sentence.slug == slug)
        )
        sentence.delete_instance()
        return "", 204
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_api_bp.route("/<target_language_code>/<slug>/rename", methods=["PUT"])
@api_auth_required
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
            (Sentence.target_language_code == target_language_code)
            & (Sentence.slug == slug)
        )

        # Update the sentence text - this will trigger slug regeneration in save()
        sentence.sentence = new_text
        sentence.slug = slugify(new_text)  # Manually update slug
            
        sentence.save()

        return jsonify({"new_text": new_text, "new_slug": sentence.slug}), 200

    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_api_bp.route(
    "/<target_language_code>/<slug>/audio/ensure", methods=["POST"]
)
@api_auth_required
def ensure_sentence_audio_api(target_language_code: str, slug: str):
    """Ensure sentence audio variants exist."""

    try:
        from config import SENTENCE_AUDIO_SAMPLES

        n = int(request.args.get("n", str(SENTENCE_AUDIO_SAMPLES)))
    except Exception:
        from config import SENTENCE_AUDIO_SAMPLES

        n = SENTENCE_AUDIO_SAMPLES

    try:
        sentence = Sentence.get(
            (Sentence.target_language_code == target_language_code)
            & (Sentence.slug == slug)
        )
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404

    try:
        variants, created = ensure_sentence_audio_variants(sentence, n=n)
    except AuthenticationRequiredForGenerationError:
        return (
            jsonify({"error": "Authentication required to generate audio"}),
            401,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Failed to ensure audio variants: {exc}"}), 500

    return jsonify({"created": created, "total": len(variants)})


@sentence_api_bp.route("/<target_language_code>/sentences", methods=["GET"])
def sentences_list_api(target_language_code: str):
    """Get all sentences for a language.

    Returns a list of all sentences for the specified language code.
    Each sentence includes basic metadata like text, translation, and slug.
    """
    # Fetch all sentences for the language
    sentences = get_all_sentences(target_language_code)

    # Transform the response to match the frontend's expected format
    for sentence in sentences:
        if "sentence" in sentence:
            sentence["text"] = sentence.pop("sentence")

    return jsonify(sentences)
