from flask import Blueprint, render_template, request, redirect, url_for
from peewee import DoesNotExist, fn, JOIN
import time
import logging
import urllib.parse

from utils.lang_utils import get_language_name
from db_models import Lemma, Wordform, LemmaExampleSentence
from utils.store_utils import load_or_generate_lemma_metadata
from utils.url_registry import endpoint_for

# Import necessary view functions
from views.core_views import languages_list_vw
from views.sourcedir_views import sourcedirs_for_language_vw

# Import search views
from views.search_views import search_word_vw, search_landing_vw

# Moving imports inside functions to avoid circular imports

lemma_views_bp = Blueprint("lemma_views", __name__, url_prefix="/lang")
logger = logging.getLogger(__name__)


@lemma_views_bp.route("/<target_language_code>/lemmas")
def lemmas_list_vw(target_language_code: str):
    """Display all lemmas for a language."""
    target_language_name = get_language_name(target_language_code)

    # Get sort parameter from request
    sort = request.args.get("sort", "alpha")

    # Get all lemmas for this language from the database using the enhanced model method
    # which now handles optimized queries and multiple sorting options
    lemmas = Lemma.get_all_lemmas_for(language_code=target_language_code, sort_by=sort)
    # TODO: Update parameter name to 'target_language_code' to match rename

    # Convert query results to the format expected by the template
    lemma_metadata = {lemma.lemma: lemma.to_dict() for lemma in lemmas}

    from utils.url_registry import endpoint_for
    from views.core_views import languages_list_vw
    from views.sourcedir_views import sourcedirs_for_language_vw

    return render_template(
        "lemmas.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        lemmas=[lemma.lemma for lemma in lemmas],  # Just pass the lemma strings
        lemma_metadata=lemma_metadata,  # Pass the metadata dictionary
        view_name=endpoint_for(lemmas_list_vw),
        current_sort=sort,
        show_commonality=True,  # We have commonality data for lemmas
        languages_vw=languages_list_vw,
        sourcedirs_for_language_vw=sourcedirs_for_language_vw,
        lemmas_list_vw=lemmas_list_vw,
    )


@lemma_views_bp.route("/<target_language_code>/lemma/<lemma>")
def get_lemma_metadata_vw(target_language_code: str, lemma: str):
    """Display metadata for a lemma."""
    # URL decode the lemma parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    lemma = urllib.parse.unquote(lemma)

    start_time = time.time()
    try:
        # Time the database fetch with prefetch
        fetch_start = time.time()
        lemma_model = (
            Lemma.select()
            .where(
                Lemma.lemma == lemma,
                Lemma.language_code == target_language_code,
            )
            .join(LemmaExampleSentence, JOIN.LEFT_OUTER)
            .get()
        )
        fetch_time = time.time() - fetch_start
        logger.info(f"Fetched lemma with joins in {fetch_time:.2f}s")

        # Load metadata, checking completeness
        dict_start = time.time()
        lemma_data = load_or_generate_lemma_metadata(
            lemma=lemma,
            target_language_code=target_language_code,
            generate_if_incomplete=True,
        )
        dict_time = time.time() - dict_start
        logger.info(f"Loaded/generated metadata in {dict_time:.2f}s")

        # Ensure all required fields are present with defaults
        default_easily_confused = [
            {
                "lemma": "",
                "explanation": "",
                "example_usage_this_target": "",
                "example_usage_this_source": "",
                "example_usage_other_target": "",
                "example_usage_other_source": "",
                "mnemonic": "",
                "notes": "",
            }
        ]

        required_fields = {
            "translations": [],
            "etymology": "",
            "commonality": 0.0,
            "guessability": 0.0,
            "register": "",
            "example_usage": [],
            "mnemonics": [],
            "related_words_phrases_idioms": [],
            "synonyms": [],
            "antonyms": [],
            "example_wordforms": [],
            "cultural_context": "",
            "easily_confused_with": default_easily_confused,
        }

        # Add any missing fields with default values
        for field, default in required_fields.items():
            if field not in lemma_data or lemma_data[field] is None:
                lemma_data[field] = default
            elif field == "easily_confused_with" and lemma_data[field]:
                # Keep existing easily_confused_with if it exists
                continue

        # Prepare metadata for template
        metadata = {
            "created_at": lemma_model.created_at,
            "updated_at": lemma_model.updated_at,
        }

        # Import here to avoid circular dependencies
        from views.wordform_views import get_wordform_metadata_vw
        from views.sentence_views import get_sentence_vw
        
        return render_template(
            "lemma.jinja",
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            lemma_metadata=lemma_data,
            dict_html="",  # TODO: Implement this
            metadata=metadata,  # Add metadata to template context
            # Add view functions for endpoint_for
            languages_vw=languages_list_vw,
            sourcedirs_for_language_vw=sourcedirs_for_language_vw,
            lemmas_list_vw=lemmas_list_vw,
            delete_lemma_vw=delete_lemma_vw,
            get_sentence_vw=get_sentence_vw,
            get_wordform_metadata_vw=get_wordform_metadata_vw,
            search_word_vw=search_word_vw,
        )
    except DoesNotExist:
        return render_template(
            "invalid_lemma.jinja",
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            lemma=lemma,
            metadata=None,  # Add metadata as None for non-existent lemmas
            # Add view functions for endpoint_for
            languages_vw=languages_list_vw,
            sourcedirs_for_language_vw=sourcedirs_for_language_vw,
            lemmas_list_vw=lemmas_list_vw,
            search_landing_vw=search_landing_vw,
        )


@lemma_views_bp.route("/<target_language_code>/lemma/<lemma>/delete", methods=["POST"])
def delete_lemma_vw(target_language_code: str, lemma: str):
    """Delete a lemma and its associated wordforms via cascade delete."""
    # URL decode the lemma parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    lemma = urllib.parse.unquote(lemma)

    try:
        lemma_model = Lemma.get(
            Lemma.lemma == lemma,
            Lemma.language_code == target_language_code,
        )
        # Simply delete the lemma - wordforms will be deleted by cascade
        lemma_model.delete_instance()
        return redirect(
            url_for(
                endpoint_for(lemmas_list_vw),
                target_language_code=target_language_code,
            )
        )
    except DoesNotExist:
        return redirect(
            url_for(
                endpoint_for(lemmas_list_vw),
                target_language_code=target_language_code,
            )
        )
