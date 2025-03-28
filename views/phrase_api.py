"""API endpoints for phrases.

All endpoints for interacting with phrases programmatically.
These endpoints follow the standard pattern:
/api/lang/phrase/...
"""

from flask import Blueprint, jsonify
from peewee import DoesNotExist
from db_models import Phrase
import urllib.parse

# Create a blueprint with standardized prefix
phrase_api_bp = Blueprint("phrase_api", __name__, url_prefix="/api/lang/phrase")


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
                & (Phrase.language_code == target_language_code)
            )
            .first()
        )

        if phrase_model is None:
            # Try to find it by a raw form
            for p in Phrase.select().where(
                Phrase.language_code == target_language_code
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
            "difficulty_level": phrase_model.difficulty_level,
            "register": phrase_model.register,
        }

        response = jsonify(preview)
        response.headers["Cache-Control"] = "public, max-age=60"  # Cache for 1 minute
        return response
    except Exception as e:
        response = jsonify({"error": "Internal Server Error", "description": str(e)})
        response.status_code = 500
        return response
