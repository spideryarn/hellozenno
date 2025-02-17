from flask import Blueprint, render_template, redirect, url_for
from gjdutils.dicts import dict_as_html
from peewee import DoesNotExist

from utils.lang_utils import get_language_name
from db_models import Wordform
from utils.vocab_llm_utils import quick_search_for_wordform

wordform_views_bp = Blueprint("wordform_views", "/")


@wordform_views_bp.route("/<target_language_code>/wordforms")
def wordforms_list(target_language_code: str):
    """Display all known wordforms for a language."""
    target_language_name = get_language_name(target_language_code)

    # Get all wordforms for this language from the database
    wordforms = (
        Wordform.select()
        .where(Wordform.language_code == target_language_code)
        .order_by(Wordform.wordform)
    )

    # Convert to list of dictionaries for template
    wordforms_d = [wordform.to_dict() for wordform in wordforms]

    # Get unique lemmas from wordforms and their IDs
    lemma_entries = {
        wordform.lemma_entry for wordform in wordforms if wordform.lemma_entry
    }

    # Load metadata for each lemma
    lemma_metadata = {}
    for lemma_entry in lemma_entries:
        lemma_metadata[lemma_entry.lemma] = lemma_entry.to_dict()

    return render_template(
        "wordforms.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        wordforms_d=wordforms_d,
        lemma_metadata=lemma_metadata,
    )


@wordform_views_bp.route("/<target_language_code>/wordform/<wordform>")
def get_wordform_metadata(target_language_code: str, wordform: str):
    """Display metadata for a wordform and link to its lemma."""
    # First try to find existing wordform in database
    try:
        wordform_model = Wordform.get(
            Wordform.wordform == wordform,
            Wordform.language_code == target_language_code,
        )
        wordform_metadata = wordform_model.to_dict()
        lemma_metadata = (
            wordform_model.lemma_entry.to_dict() if wordform_model.lemma_entry else {}
        )

        # Prepare metadata for template
        metadata = {
            "created_at": wordform_model.created_at,
            "updated_at": wordform_model.updated_at,
        }

        return render_template(
            "wordform.jinja",
            wordform_metadata=wordform_metadata,
            lemma_metadata=lemma_metadata,
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            dict_html=dict_as_html(wordform_metadata),
            metadata=metadata,  # Add metadata to template context
        )
    except DoesNotExist:
        # If not found, use quick search to get metadata
        quick_search_result, _ = quick_search_for_wordform(
            wordform, target_language_code, 1
        )

        # If the word is invalid (no lemma and possibly has misspellings)
        if quick_search_result.get("lemma") is None:
            return render_template(
                "invalid_word.jinja",
                target_language_code=target_language_code,
                target_language_name=get_language_name(target_language_code),
                wordform=wordform,
                possible_misspellings=quick_search_result.get("possible_misspellings"),
                metadata=None,  # Add metadata as None for invalid words
            )

        # Create new database entries from the quick search result
        wordform_model, _ = Wordform.get_or_create_from_metadata(
            wordform=wordform,
            language_code=target_language_code,
            metadata=quick_search_result,
        )
        wordform_metadata = wordform_model.to_dict()
        lemma_metadata = (
            wordform_model.lemma_entry.to_dict() if wordform_model.lemma_entry else {}
        )

        # Prepare metadata for template
        metadata = {
            "created_at": wordform_model.created_at,
            "updated_at": wordform_model.updated_at,
        }

        return render_template(
            "wordform.jinja",
            wordform_metadata=wordform_metadata,
            lemma_metadata=lemma_metadata,
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            dict_html=dict_as_html(wordform_metadata),
            metadata=metadata,  # Add metadata to template context
        )


@wordform_views_bp.route(
    "/<target_language_code>/wordform/<wordform>/delete", methods=["POST"]
)
def delete_wordform(target_language_code: str, wordform: str):
    """Delete a wordform from the database."""
    try:
        wordform_model = Wordform.get(
            Wordform.wordform == wordform,
            Wordform.language_code == target_language_code,
        )
        wordform_model.delete_instance()
        return redirect(
            url_for(
                "wordform_views.wordforms_list",
                target_language_code=target_language_code,
            )
        )
    except DoesNotExist:
        return redirect(
            url_for(
                "wordform_views.wordforms_list",
                target_language_code=target_language_code,
            )
        )
