"""Views for sentence management."""

from flask import (
    Blueprint,
    render_template,
    abort,
)
from peewee import DoesNotExist

from db_models import Sentence, Wordform
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_all_sentences
from utils.vocab_llm_utils import (
    create_interactive_word_links,
    normalize_text,
    extract_tokens,
)
from utils.url_registry import endpoint_for

# Import necessary view functions for templates
from views.core_views import languages_vw
from views.sourcedir_views import sourcedirs_for_language_vw


sentence_views_bp = Blueprint("sentence_views", __name__, url_prefix="/lang")


@sentence_views_bp.route("/<target_language_code>/sentences")
def sentences_list_vw(target_language_code: str):
    """Display all sentences for a language."""
    # Import here to avoid circular imports
    from views.flashcard_views import flashcard_landing_vw
    
    target_language_name = get_language_name(target_language_code)
    sentences = get_all_sentences(target_language_code)

    return render_template(
        "sentences.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        sentences=sentences,
        languages_vw=languages_vw,
        sourcedirs_for_language_vw=sourcedirs_for_language_vw,
        sentences_list_vw=sentences_list_vw,
        get_sentence_vw=get_sentence_vw,
        flashcard_landing_vw=flashcard_landing_vw,
    )


@sentence_views_bp.route("/<target_language_code>/sentence/<slug>")
def get_sentence_vw(target_language_code: str, slug: str):
    """Display a specific sentence."""
    from views.core_views import languages_vw
    from views.sourcedir_views import sourcedirs_for_language_vw

    target_language_name = get_language_name(target_language_code)

    try:
        sentence = Sentence.get(
            (Sentence.language_code == target_language_code) & (Sentence.slug == slug)
        )

        # Extract tokens from the sentence text
        tokens_in_text = extract_tokens(str(sentence.sentence))

        # Query database for all wordforms in this language
        wordforms = list(
            Wordform.select().where((Wordform.language_code == target_language_code))
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
            target_language_code=target_language_code,
        )

        # Create serializable versions of the data
        metadata = {
            "created_at": (
                sentence.created_at.isoformat() if sentence.created_at else None
            ),
            "updated_at": (
                sentence.updated_at.isoformat() if sentence.updated_at else None
            ),
        }

        # Get lemmas both from the database relationships and from the matched wordforms
        db_lemma_words = (
            sentence.lemma_words if hasattr(sentence, "lemma_words") else []
        )

        # Extract lemmas from the matched wordforms
        matched_lemmas = []
        for wf in wordforms_d:
            if (
                wf.get("lemma")
                and wf["lemma"] not in matched_lemmas
                and wf["lemma"] not in db_lemma_words
            ):
                matched_lemmas.append(wf["lemma"])

        # Combine both sources of lemmas, removing duplicates
        all_lemmas = list(set(db_lemma_words + matched_lemmas))

        sentence_data = {
            "id": sentence.id,
            "sentence": str(sentence.sentence),
            "translation": str(sentence.translation) if sentence.translation else None,
            "slug": sentence.slug,
            "language_code": sentence.language_code,
            "has_audio": bool(sentence.audio_data),
            "lemma_words": all_lemmas if all_lemmas else None,
        }

        return render_template(
            "sentence.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sentence=sentence_data,
            metadata=metadata,
            enhanced_sentence_text=enhanced_sentence_text,
            languages_vw=languages_vw,
            sourcedirs_for_language_vw=sourcedirs_for_language_vw,
            sentences_list_vw=sentences_list_vw,
        )
    except DoesNotExist:
        abort(404, description="Sentence not found")
