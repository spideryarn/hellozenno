"""API endpoints for source directories.

All endpoints for interacting with source directories programmatically.
These endpoints follow the standard pattern:
/api/lang/sourcedir/<target_language_code>/...
"""

from flask import Blueprint, request

# Create a blueprint with standardized prefix
sourcedir_api_bp = Blueprint("sourcedir_api", __name__, url_prefix="/api/lang/sourcedir")


@sourcedir_api_bp.route("/<target_language_code>", methods=["POST"])
def create_sourcedir_api(target_language_code: str):
    """Create a new source directory.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import create_sourcedir
    return create_sourcedir(target_language_code)


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>", methods=["DELETE"])
def delete_sourcedir_api(target_language_code: str, sourcedir_slug: str):
    """Delete a source directory if it's empty.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import delete_sourcedir
    return delete_sourcedir(target_language_code, sourcedir_slug)


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>/language", methods=["PUT"])
def update_sourcedir_language_api(target_language_code: str, sourcedir_slug: str):
    """Update the language of a source directory.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import update_sourcedir_language
    return update_sourcedir_language(target_language_code, sourcedir_slug)


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>/rename", methods=["PUT"])
def rename_sourcedir_api(target_language_code: str, sourcedir_slug: str):
    """Rename a source directory.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import rename_sourcedir
    return rename_sourcedir(target_language_code, sourcedir_slug)


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>/upload", methods=["POST"])
def upload_sourcedir_new_sourcefile_api(target_language_code: str, sourcedir_slug: str):
    """Handle file upload to a source directory.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import upload_sourcedir_new_sourcefile
    return upload_sourcedir_new_sourcefile(target_language_code, sourcedir_slug)


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>/update_description", methods=["PUT"])
def update_sourcedir_description_api(target_language_code: str, sourcedir_slug: str):
    """Update the description of a sourcedir.
    
    Imports and uses the same logic from sourcedir_views.py to maintain consistency.
    """
    from views.sourcedir_views import update_sourcedir_description
    return update_sourcedir_description(target_language_code, sourcedir_slug)