"""API endpoints for sourcefiles.

All endpoints for interacting with sourcefiles programmatically.
These endpoints follow the standard pattern:
/api/lang/sourcefile/...
"""

from flask import Blueprint, jsonify
import views.sourcefile_views as sourcefile_views

# Create a blueprint with standardized prefix
sourcefile_api_bp = Blueprint("sourcefile_api", __name__, url_prefix="/api/lang/sourcefile")


@sourcefile_api_bp.route("/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_individual", methods=["POST"])
def process_individual_words_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Process individual words of a sourcefile."""
    try:
        sourcefile_views.process_individual_words(target_language_code, sourcedir_slug, sourcefile_slug)
        return jsonify({"success": True})
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
        return response