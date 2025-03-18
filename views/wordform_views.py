from flask import Blueprint, render_template, redirect, url_for, request
from gjdutils.dicts import dict_as_html
from peewee import DoesNotExist, fn, JOIN
import urllib.parse

from utils.lang_utils import get_language_name
from utils.flask_view_utils import redirect_to_view
from db_models import Wordform, Lemma
from utils.vocab_llm_utils import quick_search_for_wordform

wordform_views_bp = Blueprint("wordform_views", "/", url_prefix="/lang")


@wordform_views_bp.route("/<target_language_code>/wordforms")
def wordforms_list(target_language_code: str):
    """Display all known wordforms for a language."""
    target_language_name = get_language_name(target_language_code)

    # Get sort parameter from request
    sort_by = request.args.get("sort", "alpha")

    # Get all wordforms for this language using the enhanced model method
    # which now handles all sorting options including commonality
    wordforms = Wordform.get_all_wordforms_for(
        language_code=target_language_code, sort_by=sort_by
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
        view_name="wordform_views.wordforms_list",
        current_sort=sort_by,
        show_commonality=True,  # We can show commonality by joining with Lemma
    )


@wordform_views_bp.route("/<target_language_code>/wordform/<wordform>")
def get_wordform_metadata(target_language_code: str, wordform: str):
    """Display metadata for a wordform and link to its lemma."""
    # URL decode the wordform parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    wordform = urllib.parse.unquote(wordform)

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
        search_result, _ = quick_search_for_wordform(
            wordform, target_language_code, 1
        )
        
        # Count total matches from both result types
        target_matches = search_result["target_language_results"]["matches"]
        english_matches = search_result["english_results"]["matches"]
        total_matches = len(target_matches) + len(english_matches)
        
        # Check for possible misspellings
        target_misspellings = search_result["target_language_results"]["possible_misspellings"]
        english_misspellings = search_result["english_results"]["possible_misspellings"]
        
        # If there are multiple matches or misspellings, show search results
        if total_matches > 1 or target_misspellings or english_misspellings:
            return render_template(
                "translation_search_results.jinja",
                target_language_code=target_language_code,
                target_language_name=get_language_name(target_language_code),
                search_term=wordform,
                target_language_results=search_result["target_language_results"],
                english_results=search_result["english_results"],
            )
        
        # If there's exactly one match, redirect to that wordform
        elif total_matches == 1:
            # Get the single match (either from target or english results)
            match = target_matches[0] if target_matches else english_matches[0]
            match_wordform = match.get("target_language_wordform")
            
            if match_wordform:
                # Simply redirect to the wordform URL - it will be created when it's viewed
                return redirect(url_for(
                    "wordform_views.get_wordform_metadata",
                    target_language_code=target_language_code,
                    wordform=match_wordform
                ))
        
        # If no matches or misspellings, show invalid word template
        else:
            return render_template(
                "invalid_word.jinja",
                target_language_code=target_language_code,
                target_language_name=get_language_name(target_language_code),
                wordform=wordform,
                possible_misspellings=target_misspellings,
                metadata=None,
            )