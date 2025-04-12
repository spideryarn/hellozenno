"""API endpoints for sourcefile processing.

These endpoints handle individual processing steps for sourcefiles.
"""

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
)
from peewee import DoesNotExist

from config import (
    DEFAULT_LANGUAGE_LEVEL,
    DEFAULT_MAX_NEW_PHRASES_FOR_PROCESSED_SOURCEFILE,
    DEFAULT_MAX_NEW_WORDS_FOR_PROCESSED_SOURCEFILE,
)
from db_models import (
    SourcefilePhrase,
    SourcefileWordform,
)
from utils.sourcefile_utils import (
    _get_sourcefile_entry,
    ensure_text_extracted,
    ensure_translation,
    ensure_tricky_wordforms,
    ensure_tricky_phrases,
)
from utils.types import LanguageLevel
from typing import get_args


# Create a blueprint with standardized prefix
sourcefile_processing_api_bp = Blueprint(
    "sourcefile_processing_api", __name__, url_prefix="/api/lang/sourcefile"
)


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/extract_text",
    methods=["POST"],
)
def extract_text_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Extract text from a sourcefile (image or audio)."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Extract text
        sourcefile_entry = ensure_text_extracted(sourcefile_entry)

        return jsonify({
            "success": True,
            "has_text": bool(sourcefile_entry.text_target),
        })

    except Exception as e:
        current_app.logger.error(f"Error extracting text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/translate",
    methods=["POST"],
)
def translate_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Translate the text of a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Ensure we have text to translate
        if not sourcefile_entry.text_target:
            return jsonify({"success": False, "error": "No text to translate"}), 400

        # Translate the text
        sourcefile_entry = ensure_translation(sourcefile_entry)

        return jsonify({
            "success": True,
            "has_translation": bool(sourcefile_entry.text_english),
        })

    except Exception as e:
        current_app.logger.error(f"Error translating text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_wordforms",
    methods=["POST"],
)
def process_wordforms_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process wordforms for a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get processing parameters from request or use defaults
        data = request.get_json() or {}

        max_new_words = int(data.get("max_new_words", DEFAULT_MAX_NEW_WORDS_FOR_PROCESSED_SOURCEFILE))
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)
        assert language_level in get_args(LanguageLevel), f"Invalid language level: {language_level}"

        # Process wordforms
        sourcefile_entry, _ = ensure_tricky_wordforms(
            sourcefile_entry,
            language_level=language_level,  # type: ignore
            max_new_words=max_new_words,
        )

        # Count the wordforms for response
        wordforms_count = SourcefileWordform.select().where(
            SourcefileWordform.sourcefile == sourcefile_entry
        ).count()

        return jsonify({
            "success": True,
            "params": {
                "max_new_words": max_new_words,
                "language_level": language_level,
            },
            "wordforms_count": wordforms_count
        })

    except Exception as e:
        current_app.logger.error(f"Error processing wordforms: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_phrases",
    methods=["POST"],
)
def process_phrases_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process phrases for a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get processing parameters from request or use defaults
        data = request.get_json() or {}

        max_new_phrases = int(data.get("max_new_phrases", DEFAULT_MAX_NEW_PHRASES_FOR_PROCESSED_SOURCEFILE))
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)
        assert language_level in get_args(LanguageLevel), f"Invalid language level: {language_level}"

        # Process phrases
        sourcefile_entry, _ = ensure_tricky_phrases(
            sourcefile_entry,
            language_level=language_level,  # type: ignore
            max_new_phrases=max_new_phrases,
        )

        # Count the phrases for response
        phrases_count = SourcefilePhrase.select().where(
            SourcefilePhrase.sourcefile == sourcefile_entry
        ).count()

        return jsonify({
            "success": True,
            "params": {
                "max_new_phrases": max_new_phrases,
                "language_level": language_level,
            },
            "phrases_count": phrases_count
        })

    except Exception as e:
        current_app.logger.error(f"Error processing phrases: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/status",
    methods=["GET"],
)
def sourcefile_status_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Get the processing status of a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Check what processing has been completed
        status = {
            "has_text": bool(sourcefile_entry.text_target),
            "has_translation": bool(sourcefile_entry.text_english),
            "wordforms_count": SourcefileWordform.select().where(
                SourcefileWordform.sourcefile == sourcefile_entry
            ).count(),
            "phrases_count": SourcefilePhrase.select().where(
                SourcefilePhrase.sourcefile == sourcefile_entry
            ).count(),
        }

        return jsonify({
            "success": True,
            "status": status,
        })

    except Exception as e:
        current_app.logger.error(f"Error getting sourcefile status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500