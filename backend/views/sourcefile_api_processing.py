"""API endpoints for sourcefile processing.

These endpoints handle individual processing steps for sourcefiles.
"""

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
)

from config import (
    DEFAULT_LANGUAGE_LEVEL,
    DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING,
    DEFAULT_MAX_NEW_WORDS_PER_PROCESSING,
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
    get_incomplete_lemmas_for_sourcefile,
)
from utils.types import LanguageLevel
from typing import get_args

# Import the auth decorator
from utils.auth_utils import api_auth_required


# Create a blueprint with standardized prefix
sourcefile_processing_api_bp = Blueprint(
    "sourcefile_processing_api", __name__, url_prefix="/api/lang/sourcefile"
)


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/extract_text",
    methods=["POST"],
)
@api_auth_required
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

        return jsonify(
            {
                "success": True,
                "has_text": bool(sourcefile_entry.text_target),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error extracting text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/translate",
    methods=["POST"],
)
@api_auth_required
def translate_api(target_language_code: str, sourcedir_slug: str, sourcefile_slug: str):
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

        return jsonify(
            {
                "success": True,
                "has_translation": bool(sourcefile_entry.text_english),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error translating text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_wordforms",
    methods=["POST"],
)
@api_auth_required
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

        # Validate max_new_words parameter
        try:
            max_new_words = int(
                data.get("max_new_words", DEFAULT_MAX_NEW_WORDS_PER_PROCESSING)
            )
            if max_new_words < 0:
                return jsonify({"success": False, "error": "max_new_words must be non-negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "max_new_words must be a valid integer"}), 400

        # Validate language_level parameter
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)
        valid_levels = get_args(LanguageLevel)
        if language_level not in valid_levels:
            return jsonify({
                "success": False, 
                "error": f"Invalid language level: {language_level}. Must be one of: {', '.join(valid_levels)}"
            }), 400

        # Process wordforms
        sourcefile_entry, _ = ensure_tricky_wordforms(
            sourcefile_entry,
            language_level=language_level,  # type: ignore
            max_new_words=max_new_words,
        )

        # Count the wordforms for response
        wordforms_count = (
            SourcefileWordform.select()
            .where(SourcefileWordform.sourcefile == sourcefile_entry)
            .count()
        )

        return jsonify(
            {
                "success": True,
                "params": {
                    "max_new_words": max_new_words,
                    "language_level": language_level,
                },
                "wordforms_count": wordforms_count,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error processing wordforms: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_processing_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_phrases",
    methods=["POST"],
)
@api_auth_required
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

        # Validate max_new_phrases parameter
        try:
            max_new_phrases = int(
                data.get("max_new_phrases", DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING)
            )
            if max_new_phrases < 0:
                return jsonify({"success": False, "error": "max_new_phrases must be non-negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "max_new_phrases must be a valid integer"}), 400

        # Validate language_level parameter
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)
        valid_levels = get_args(LanguageLevel)
        if language_level not in valid_levels:
            return jsonify({
                "success": False, 
                "error": f"Invalid language level: {language_level}. Must be one of: {', '.join(valid_levels)}"
            }), 400

        # Process phrases
        sourcefile_entry, _ = ensure_tricky_phrases(
            sourcefile_entry,
            language_level=language_level,  # type: ignore
            max_new_phrases=max_new_phrases,
        )

        # Count the phrases for response
        phrases_count = (
            SourcefilePhrase.select()
            .where(SourcefilePhrase.sourcefile == sourcefile_entry)
            .count()
        )

        return jsonify(
            {
                "success": True,
                "params": {
                    "max_new_phrases": max_new_phrases,
                    "language_level": language_level,
                },
                "phrases_count": phrases_count,
            }
        )

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
            "wordforms_count": SourcefileWordform.select()
            .where(SourcefileWordform.sourcefile == sourcefile_entry)
            .count(),
            "phrases_count": SourcefilePhrase.select()
            .where(SourcefilePhrase.sourcefile == sourcefile_entry)
            .count(),
        }

        # Get information about incomplete lemmas
        incomplete_lemmas = get_incomplete_lemmas_for_sourcefile(sourcefile_entry)
        lemma_data = []

        # Include basic lemma information for each incomplete lemma
        for lemma in incomplete_lemmas:
            lemma_data.append(
                {
                    "lemma": lemma.lemma,
                    "part_of_speech": lemma.part_of_speech,
                    "translations": lemma.translations,
                }
            )

        status["incomplete_lemmas"] = lemma_data
        status["incomplete_lemmas_count"] = len(lemma_data)

        return jsonify(
            {
                "success": True,
                "status": status,
            }
        )

    except Exception as e:
        # Log the full traceback
        current_app.logger.exception(
            f"Error getting sourcefile status for {target_language_code}/{sourcedir_slug}/{sourcefile_slug}"
        )
        # Return 500 with the error message (as before)
        return jsonify({"success": False, "error": str(e)}), 500
