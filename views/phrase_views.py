from flask import Blueprint, render_template, abort, request
from db_models import Phrase
from peewee import DoesNotExist, fn
from lang_utils import get_language_name
from vocab_llm_utils import extract_phrases_from_text

phrase_views_bp = Blueprint("phrase_views", __name__)


@phrase_views_bp.route("/<target_language_code>/phrases")
def phrases_list(target_language_code):
    """Show list of phrases for a language."""
    sort_by = request.args.get("sort", "alpha")  # Default to alphabetical
    target_language_name = get_language_name(target_language_code)

    # Query phrases from database
    query = Phrase.select().where(Phrase.language_code == target_language_code)

    if sort_by == "date":
        # Sort by modification time, newest first
        query = query.order_by(fn.COALESCE(Phrase.updated_at, Phrase.created_at).desc())
    else:
        # Default alphabetical sort
        query = query.order_by(Phrase.canonical_form)

    return render_template(
        "phrases.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        phrases=query,
        current_sort=sort_by,
    )


@phrase_views_bp.route("/<target_language_code>/phrase/<canonical_form>")
def get_phrase_metadata(target_language_code, canonical_form):
    """Get metadata for a specific phrase."""
    target_language_name = get_language_name(target_language_code)

    try:
        # First try to find existing phrase in database
        phrase = Phrase.get(
            (Phrase.language_code == target_language_code)
            & (Phrase.canonical_form == canonical_form)
        )
    except DoesNotExist:
        # If not found, generate new metadata using LLM
        phrases_data, _ = extract_phrases_from_text(
            canonical_form, target_language_name=target_language_name
        )

        # Get the first phrase's metadata or create a default one
        metadata = next(
            (
                p
                for p in phrases_data.get("phrases", [])
                if p.get("canonical_form") == canonical_form
            ),
            None,
        )

        if metadata is None:
            # If no metadata could be generated, return 404
            abort(404)

        # Create new database entry
        phrase = Phrase.create(
            canonical_form=canonical_form,
            language_code=target_language_code,
            raw_forms=[canonical_form],  # At least include the canonical form
            translations=metadata.get("translations", []),
            part_of_speech=metadata.get("part_of_speech", "phrase"),
            register=metadata.get("register", "neutral"),
            commonality=metadata.get("commonality", 0.5),
            guessability=metadata.get("guessability", 0.5),
            etymology=metadata.get("etymology", ""),
            cultural_context=metadata.get("cultural_context", ""),
            mnemonics=metadata.get("mnemonics", []),
            component_words=metadata.get("component_words", []),
            usage_notes=metadata.get("usage_notes", ""),
            difficulty_level=metadata.get("difficulty_level", "intermediate"),
        )

    # Prepare metadata for template
    metadata = {
        "created_at": phrase.created_at,
        "updated_at": phrase.updated_at,
    }

    return render_template(
        "phrase.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        phrase=phrase,
        metadata=metadata,  # Add metadata to template context
    )
