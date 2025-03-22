"""API endpoints for sourcefiles.

All endpoints for interacting with sourcefiles programmatically.
These endpoints follow the standard pattern:
/api/lang/sourcefile/...
"""

from flask import Blueprint, jsonify, request
import views.sourcefile_views as sourcefile_views

# Create a blueprint with standardized prefix
sourcefile_api_bp = Blueprint(
    "sourcefile_api", __name__, url_prefix="/api/lang/sourcefile"
)


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_individual",
    methods=["POST"],
)
def process_individual_words_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Process individual words of a sourcefile."""
    try:
        sourcefile_views.process_individual_words_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
        return jsonify({"success": True})
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/update_description",
    methods=["PUT"],
)
def update_sourcefile_description_api(
    target_language_code, sourcedir_slug, sourcefile_slug
):
    """Update description of a sourcefile."""
    try:
        return sourcefile_views.update_sourcefile_description_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/move", methods=["PUT"]
)
def move_sourcefile_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Move a sourcefile to a different source directory."""
    try:
        return sourcefile_views.move_sourcefile_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>", methods=["DELETE"]
)
def delete_sourcefile_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Delete a sourcefile."""
    try:
        return sourcefile_views.delete_sourcefile_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/rename", methods=["PUT"]
)
def rename_sourcefile_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Rename a sourcefile."""
    try:
        return sourcefile_views.rename_sourcefile_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/create_from_text", methods=["POST"]
)
def create_sourcefile_from_text_api(target_language_code, sourcedir_slug):
    """Create a new sourcefile from text."""
    try:
        return sourcefile_views.create_sourcefile_from_text_vw(
            target_language_code, sourcedir_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate_audio",
    methods=["POST"],
)
def generate_sourcefile_audio_api(
    target_language_code, sourcedir_slug, sourcefile_slug
):
    """Generate audio for a sourcefile."""
    try:
        return sourcefile_views.generate_sourcefile_audio_vw(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response
