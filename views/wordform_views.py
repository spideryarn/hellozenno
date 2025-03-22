from flask import Blueprint, render_template, redirect, url_for, request
from gjdutils.dicts import dict_as_html
from peewee import DoesNotExist
import urllib.parse

from utils.lang_utils import get_language_name
from db_models import Wordform
from utils.vocab_llm_utils import quick_search_for_wordform
from utils.url_registry import endpoint_for

# Import necessary view functions
from views.core_views import languages_list_vw
from views.sourcedir_views import sourcedirs_for_language_vw

# Moving search_views and lemma_views imports inside functions to avoid circular imports

wordform_views_bp = Blueprint("wordform_views", "/", url_prefix="/lang")


@wordform_views_bp.route("/<target_language_code>/wordforms/")
def wordforms_list_vw(target_language_code: str):
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

    # Import necessary view functions inside this function to avoid circular imports
    from views.core_views import languages_list_vw
    from views.sourcedir_views import sourcedirs_for_language_vw
    
    # We need this one for the _wordforms_list.jinja template
    # The circular import is handled by importing inside the function
    from views.wordform_views import get_wordform_metadata_vw

    return render_template(
        "wordforms.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        wordforms_d=wordforms_d,
        lemma_metadata=lemma_metadata,
        view_name=endpoint_for(wordforms_list_vw),
        current_sort=sort_by,
        show_commonality=True,  # We can show commonality by joining with Lemma
        # Add view functions for endpoint_for
        languages_list_vw=languages_list_vw,
        sourcedirs_for_language_vw=sourcedirs_for_language_vw,
        wordforms_list_vw=wordforms_list_vw,
        get_wordform_metadata_vw=get_wordform_metadata_vw,  # Add this view function that's used in _wordforms_list.jinja
    )


@wordform_views_bp.route("/<target_language_code>/wordform/<wordform>")
def get_wordform_metadata_vw(target_language_code: str, wordform: str):
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

        # Import here to avoid circular dependencies
        from views.lemma_views import get_lemma_metadata_vw

        return render_template(
            "wordform.jinja",
            wordform_metadata=wordform_metadata,
            lemma_metadata=lemma_metadata,
            target_language_code=target_language_code,
            target_language_name=get_language_name(target_language_code),
            dict_html=dict_as_html(wordform_metadata),
            metadata=metadata,  # Add metadata to template context
            # Add view functions for endpoint_for
            languages_list_vw=languages_list_vw,
            sourcedirs_for_language_vw=sourcedirs_for_language_vw,
            wordforms_list_vw=wordforms_list_vw,
            delete_wordform_vw=delete_wordform_vw,
            get_lemma_metadata_vw=get_lemma_metadata_vw,
        )
    except DoesNotExist:
        # If not found, use quick search to get metadata
        search_result, _ = quick_search_for_wordform(wordform, target_language_code, 1)

        # Count total matches from both result types
        target_matches = search_result["target_language_results"]["matches"]
        english_matches = search_result["english_results"]["matches"]
        total_matches = len(target_matches) + len(english_matches)

        # Check for possible misspellings
        target_misspellings = search_result["target_language_results"][
            "possible_misspellings"
        ]
        english_misspellings = search_result["english_results"]["possible_misspellings"]

        # If there are multiple matches or misspellings, show search results
        if total_matches > 1 or target_misspellings or english_misspellings:
            # Import here to avoid circular dependencies
            from views.lemma_views import get_lemma_metadata_vw
            from views.search_views import search_landing_vw, search_word_vw

            return render_template(
                "translation_search_results.jinja",
                target_language_code=target_language_code,
                target_language_name=get_language_name(target_language_code),
                search_term=wordform,
                target_language_results=search_result["target_language_results"],
                english_results=search_result["english_results"],
                # Add view functions for endpoint_for
                languages_list_vw=languages_list_vw,
                sourcedirs_for_language_vw=sourcedirs_for_language_vw,
                wordforms_list_vw=wordforms_list_vw,
                get_wordform_metadata_vw=get_wordform_metadata_vw,
                get_lemma_metadata_vw=get_lemma_metadata_vw,
                search_landing_vw=search_landing_vw,
                search_word_vw=search_word_vw,
            )

        # If there's exactly one match, redirect to that wordform
        elif total_matches == 1:
            # Get the single match (either from target or english results)
            match = target_matches[0] if target_matches else english_matches[0]
            match_wordform = match.get("target_language_wordform")

            if match_wordform:
                # First create the wordform in the database to avoid redirect loops
                # Convert from new response format to metadata format expected by get_or_create_from_metadata
                metadata = {
                    "wordform": match_wordform,
                    "lemma": match.get("target_language_lemma"),
                    "part_of_speech": match.get("part_of_speech"),
                    "translations": match.get("english", []),
                    "inflection_type": match.get("inflection_type"),
                    "possible_misspellings": None,
                }

                # Create the wordform in the database
                Wordform.get_or_create_from_metadata(
                    wordform=match_wordform,
                    language_code=target_language_code,
                    metadata=metadata,
                )

                # Now redirect to the wordform URL
                return redirect(
                    url_for(
                        endpoint_for(get_wordform_metadata_vw),
                        target_language_code=target_language_code,
                        wordform=match_wordform,
                    )
                )

        # If no matches or misspellings, show invalid word template
        else:
            # Import here to avoid circular dependencies
            from views.search_views import search_landing_vw

            return render_template(
                "invalid_word.jinja",
                target_language_code=target_language_code,
                target_language_name=get_language_name(target_language_code),
                wordform=wordform,
                possible_misspellings=target_misspellings,
                metadata=None,
                # Add view functions for endpoint_for
                languages_list_vw=languages_list_vw,
                sourcedirs_for_language_vw=sourcedirs_for_language_vw,
                wordforms_list_vw=wordforms_list_vw,
                get_wordform_metadata_vw=get_wordform_metadata_vw,
                search_landing_vw=search_landing_vw,
            )


@wordform_views_bp.route(
    "/<target_language_code>/wordform/<wordform>/delete", methods=["POST"]
)
def delete_wordform_vw(target_language_code: str, wordform: str):
    """Delete a wordform from the database."""
    # URL decode the wordform parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    wordform = urllib.parse.unquote(wordform)

    try:
        wordform_model = Wordform.get(
            Wordform.wordform == wordform,
            Wordform.language_code == target_language_code,
        )
        wordform_model.delete_instance()
        return redirect(
            url_for(
                endpoint_for(wordforms_list_vw),
                target_language_code=target_language_code,
            )
        )
    except DoesNotExist:
        return redirect(
            url_for(
                endpoint_for(wordforms_list_vw),
                target_language_code=target_language_code,
            )
        )
