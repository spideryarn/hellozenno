"""Views for sentence management."""

import io
from flask import (
    Blueprint,
    send_file,
    jsonify,
    render_template,
    request,
    abort,
)
from peewee import DoesNotExist

from db_models import Sentence, Wordform
from utils.audio_utils import ensure_model_audio_data
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_all_sentences, get_random_sentence
from slugify import slugify
from utils.vocab_llm_utils import (
    create_interactive_word_links,
    normalize_text,
    extract_tokens,
)


sentence_views_bp = Blueprint("sentence_views", __name__)


@sentence_views_bp.route("/<language_code>/sentences")
def sentences_list(language_code: str):
    """Display all sentences for a language."""
    target_language_name = get_language_name(language_code)
    sentences = get_all_sentences(language_code)

    return render_template(
        "sentences.jinja",
        target_language_code=language_code,
        target_language_name=target_language_name,
        sentences=sentences,
    )


@sentence_views_bp.route("/api/<language_code>/sentences/random")
def get_random_sentence_api(language_code: str):
    """Get a random sentence for the given language.

    Supports filtering by lemmas via the lemmas[] query parameter.
    Returns 404 if no matching sentences are found.
    """
    # Get lemmas from query params if provided
    lemmas = request.args.getlist("lemmas[]")

    # Get random sentence
    sentence = get_random_sentence(
        target_language_code=language_code, required_lemmas=lemmas if lemmas else None
    )

    if not sentence:
        return jsonify({"error": "No matching sentences found"}), 404

    return jsonify(sentence)


@sentence_views_bp.route("/api/<language_code>/sentences/<int:sentence_id>/audio")
def get_sentence_audio(language_code: str, sentence_id: int):
    """Serve audio data for a sentence from the database.

    Args:
        language_code: ISO language code
        sentence_id: Database ID of the sentence

    Returns:
        Audio file response or 404 if not found
    """
    try:
        sentence = Sentence.get(
            (Sentence.id == sentence_id) & (Sentence.language_code == language_code)  # type: ignore
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


@sentence_views_bp.route("/<language_code>/sentence/<slug>")
def get_sentence(language_code: str, slug: str):
    """Display a specific sentence."""
    target_language_name = get_language_name(language_code)

    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
        )

        # Extract tokens from the sentence text
        tokens_in_text = extract_tokens(str(sentence.sentence))

        # Query database for all wordforms in this language
        wordforms = list(
            Wordform.select().where((Wordform.language_code == language_code))
        )

        # Filter wordforms in Python using normalize_text
        normalized_tokens = {normalize_text(t) for t in tokens_in_text}
        wordforms = [
            wf for wf in wordforms if normalize_text(wf.wordform) in normalized_tokens
        ]

        # Convert to dictionary format
        wordforms_d = []
        for wordform in wordforms:
            wordform_d = wordform.to_dict()
            wordform_d["centrality"] = 0.3  # Default centrality
            wordform_d["ordering"] = len(wordforms_d) + 1
            wordforms_d.append(wordform_d)

        # Create enhanced text with interactive word links
        enhanced_sentence_text, found_wordforms = create_interactive_word_links(
            text=str(sentence.sentence),
            wordforms=wordforms_d,
            target_language_code=language_code,
        )

        metadata = {
            "created_at": sentence.created_at,
            "updated_at": sentence.updated_at,
        }
        return render_template(
            "sentence.jinja",
            target_language_code=language_code,
            target_language_name=target_language_name,
            sentence=sentence,
            metadata=metadata,
            enhanced_sentence_text=enhanced_sentence_text,
        )
    except DoesNotExist:
        abort(404, description="Sentence not found")


@sentence_views_bp.route("/api/sentence/<language_code>/<slug>", methods=["DELETE"])
def delete_sentence(language_code: str, slug: str):
    """Delete a sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
        )
        sentence.delete_instance()
        return "", 204
    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_views_bp.route("/api/sentence/<language_code>/<slug>/rename", methods=["PUT"])
def rename_sentence(language_code: str, slug: str):
    """Rename/edit a sentence."""
    try:
        data = request.get_json()
        if not data or "new_text" not in data:
            return jsonify({"error": "Missing new_text parameter"}), 400

        new_text = data["new_text"].strip()
        if not new_text:
            return jsonify({"error": "Invalid sentence text"}), 400

        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
        )

        # Update the sentence text - this will trigger slug regeneration in save()
        sentence.sentence = new_text
        sentence.slug = slugify(new_text)  # Manually update slug
        sentence.save()

        return jsonify({"new_text": new_text, "new_slug": sentence.slug}), 200

    except DoesNotExist:
        return jsonify({"error": "Sentence not found"}), 404


@sentence_views_bp.route(
    "/api/sentence/<language_code>/<slug>/generate_audio", methods=["POST"]
)
def generate_sentence_audio(language_code: str, slug: str):
    """Generate audio for a sentence."""
    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
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
