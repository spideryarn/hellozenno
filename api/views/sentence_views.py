"""Views for sentence management."""

from flask import (
    Blueprint,
    render_template,
    abort,
)
from peewee import DoesNotExist

from api.db_models import Sentence, Wordform
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_all_sentences, get_detailed_sentence_data
from utils.vocab_llm_utils import (
    create_interactive_word_links,
    extract_tokens,
)
from utils.url_registry import endpoint_for

# Import necessary view functions for templates
from utils.word_utils import normalize_text
from views.languages_views import languages_list_vw
from views.sourcedir_views import sourcedirs_for_language_vw


sentence_views_bp = Blueprint("sentence_views", __name__, url_prefix="/language")


@sentence_views_bp.route("/<target_language_code>/sentences")
def sentences_list_vw(target_language_code: str):
    """Display all sentences for a language."""
    target_language_name = get_language_name(target_language_code)
    sentences = get_all_sentences(target_language_code)

    return render_template(
        "sentences.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        sentences=sentences,
    )


@sentence_views_bp.route("/<target_language_code>/sentence/<slug>")
def get_sentence_vw(target_language_code: str, slug: str):
    """Display a specific sentence."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Use the shared utility function to get sentence data
        data = get_detailed_sentence_data(target_language_code, slug)

        return render_template(
            "sentence.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sentence=data["sentence"],
            metadata=data["metadata"],
            enhanced_sentence_text=data["enhanced_sentence_text"],
            languages_list_vw=languages_list_vw,
            sourcedirs_for_language_vw=sourcedirs_for_language_vw,
            sentences_list_vw=sentences_list_vw,
        )
    except DoesNotExist:
        abort(404, description="Sentence not found")
