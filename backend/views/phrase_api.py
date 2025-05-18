"""API endpoints for phrases.

All endpoints for interacting with phrases programmatically.
These endpoints follow the standard pattern:
/api/lang/phrase/...
"""

from flask import Blueprint, jsonify, request
from peewee import DoesNotExist
from utils.auth_utils import api_auth_required
from db_models import Phrase
import urllib.parse
from utils.phrase_utils import get_phrases_query, get_phrase_by_slug


# Create a blueprint with standardized prefix
phrase_api_bp = Blueprint("phrase_api", __name__, url_prefix="/api/lang/phrase")


@phrase_api_bp.route("/<target_language_code>/phrases")
def phrases_list_api(target_language_code: str):
    """Get all phrases for a language.

    Returns a list of all phrases for the specified language code.
    Supports sorting via the 'sort' query parameter:
    - 'alpha' (default): Sort alphabetically
    - 'date': Sort by last updated date
    """
    # Get sort parameter from request
    sort_by = request.args.get("sort", "alpha")  # Default to alphabetical

    # Get the query using the shared utility function
    query = get_phrases_query(target_language_code, sort_by)

    # Convert query results to a list of dictionaries using Peewee's dicts() method
    phrases_list = list(query.dicts())

    # Format datetime fields for JSON serialization
    for phrase in phrases_list:
        if phrase.get("created_at"):
            phrase["created_at"] = phrase["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        if phrase.get("updated_at"):
            phrase["updated_at"] = phrase["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(phrases_list)


@phrase_api_bp.route("/<target_language_code>/preview/<phrase>")
def phrase_preview_api(target_language_code: str, phrase: str):
    """Get preview data for phrase tooltips."""
    # Fix URL encoding issues with Vercel by explicitly unquoting the phrase parameter
    phrase = urllib.parse.unquote(phrase)

    try:
        # Try to find the phrase in the database
        phrase_model = (
            Phrase.select()
            .where(
                (Phrase.canonical_form == phrase)
                & (Phrase.target_language_code == target_language_code)
            )
            .first()
        )

        if phrase_model is None:
            # Try to find it by a raw form
            for p in Phrase.select().where(
                Phrase.target_language_code == target_language_code
            ):
                if phrase in p.raw_forms:
                    phrase_model = p
                    break

        if phrase_model is None:
            response = jsonify(
                {"error": "Not Found", "description": f"Phrase '{phrase}' not found"}
            )
            response.status_code = 404
            return response

        # Create preview data
        preview = {
            "canonical_form": phrase_model.canonical_form,
            "translations": phrase_model.translations,
            "part_of_speech": phrase_model.part_of_speech,
            "usage_notes": phrase_model.usage_notes,
            "language_level": phrase_model.language_level,
            "register": phrase_model.register,
        }

        response = jsonify(preview)
        response.headers["Cache-Control"] = "public, max-age=60"  # Cache for 1 minute
        return response
    except Exception as e:
        response = jsonify({"error": "Internal Server Error", "description": str(e)})
        response.status_code = 500
        return response


@phrase_api_bp.route("/<target_language_code>/detail/<slug>")
def get_phrase_metadata_api(target_language_code: str, slug: str):
    """Get metadata for a specific phrase using its slug.

    Returns detailed information about a phrase.
    """
    try:
        # Use the utility function to find phrase by slug
        phrase = get_phrase_by_slug(target_language_code, slug)

        # Convert the model to a dictionary and return as JSON
        return jsonify(phrase.to_dict())

    except DoesNotExist:
        response = jsonify(
            {
                "error": "Not Found",
                "description": f"Phrase with slug '{slug}' not found",
            }
        )
        response.status_code = 404
        return response


@phrase_api_bp.route("/<target_language_code>/detail/<slug>/delete", methods=["POST"])
@api_auth_required
def delete_phrase_api(target_language_code: str, slug: str):
    """Delete a specific phrase using its slug.

    Request must be a POST request.
    """
    try:
        phrase = get_phrase_by_slug(target_language_code, slug)
        phrase_text = phrase.canonical_form
        phrase.delete_instance()

        return jsonify(
            {
                "success": True,
                "message": f"Phrase '{phrase_text}' has been deleted.",
                "deleted_phrase": phrase_text,
            }
        )

    except DoesNotExist:
        response = jsonify(
            {
                "error": "Not Found",
                "description": f"Phrase with slug '{slug}' not found",
            }
        )
        response.status_code = 404
        return response
