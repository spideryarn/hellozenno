from flask import Blueprint, render_template, redirect, url_for, request
from gjdutils.dicts import dict_as_html
import urllib.parse

from utils.lang_utils import get_language_name
from db_models import Wordform
from utils.vocab_llm_utils import quick_search_for_wordform
from utils.url_registry import endpoint_for
from utils.word_utils import get_wordform_metadata

# Import necessary view functions
from views.languages_views import languages_list_vw
from views.sourcedir_views import sourcedirs_for_language_vw

# Moving search_views and lemma_views imports inside functions to avoid circular imports

wordform_views_bp = Blueprint("wordform_views", "/", url_prefix="/language")


@wordform_views_bp.route("/<target_language_code>/wordforms/")
def wordforms_list_vw(target_language_code: str):
    """Display all known wordforms for a language."""
    target_language_name = get_language_name(target_language_code)

    # Get sort parameter from request
    sort_by = request.args.get("sort", "alpha")

    # Get all wordforms for this language using the enhanced model method
    # which now handles all sorting options including commonality
    wordforms = Wordform.get_all_wordforms_for(
        target_language_code=target_language_code, sort_by=sort_by
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
        current_sort=sort_by,
        show_commonality=True,  # We can show commonality by joining with Lemma
    )


@wordform_views_bp.route("/<target_language_code>/wordform/<wordform>")
def get_wordform_metadata_vw(target_language_code: str, wordform: str):
    """Display metadata for a wordform and link to its lemma."""
    # URL decode the wordform parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    wordform = urllib.parse.unquote(wordform)

    # Use the shared utility function to find or create the wordform
    from utils.word_utils import find_or_create_wordform

    result = find_or_create_wordform(target_language_code, wordform)

    # Handle different status responses
    if result["status"] == "found":
        data = result["data"]
        return render_template(
            "wordform.jinja",
            wordform_metadata=data["wordform_metadata"],
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            dict_html=dict_as_html(data["wordform_metadata"]),
            metadata=data["metadata"],  # Add metadata to template context
        )
    elif result["status"] == "multiple_matches":
        data = result["data"]
        return render_template(
            "translation_search_results.jinja",
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            search_term=data["search_term"],
            target_language_results=data["target_language_results"],
            english_results=data["english_results"],
        )
    elif result["status"] == "redirect":
        data = result["data"]
        # Redirect to the wordform URL
        return redirect(
            url_for(
                endpoint_for(get_wordform_metadata_vw),
                target_language_code=target_language_code,
                wordform=data["redirect_to"],
            )
        )
    else:  # invalid
        data = result["data"]
        return render_template(
            "invalid_word.jinja",
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            wordform=data["wordform"],
            possible_misspellings=data["possible_misspellings"],
            metadata=None,
        )
