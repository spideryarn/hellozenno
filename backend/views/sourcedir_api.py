"""API endpoints for source directories.

All endpoints for interacting with source directories programmatically.
These endpoints follow the standard pattern:
/api/lang/sourcedir/<target_language_code>/...
"""

import datetime
from flask import Blueprint, flash, jsonify, redirect, request, url_for
from peewee import DoesNotExist
from slugify import slugify

from config import (
    MAX_AUDIO_SIZE_UPLOAD_ALLOWED,
    MAX_IMAGE_SIZE_UPLOAD_ALLOWED,
    MAX_TEXT_SIZE_UPLOAD_ALLOWED,
    MAX_NUMBER_UPLOAD_FILES,
    SOURCE_EXTENSIONS,
    TEXT_SOURCE_EXTENSIONS,
)
from db_models import Sourcedir, Sourcefile
from utils.lang_utils import VALID_target_language_codeS
from utils.sourcedir_utils import (
    _get_sourcedir_entry,
    allowed_file,
    get_sourcedirs_for_language,
    get_sourcefiles_for_sourcedir,
)
from loguru import logger
from utils.sourcefile_utils import process_uploaded_file
from utils.auth_utils import api_auth_required

# Create a blueprint with standardized prefix
sourcedir_api_bp = Blueprint(
    "sourcedir_api", __name__, url_prefix="/api/lang/sourcedir"
)


@sourcedir_api_bp.route("/<target_language_code>", methods=["POST"])
@api_auth_required
def create_sourcedir_api(target_language_code: str):
    """Create a new source directory."""
    data = request.get_json()
    if not data or "path" not in data:
        return jsonify({"error": "Missing path parameter"}), 400

    path = data["path"].strip()
    if not path:
        return jsonify({"error": "Path cannot be empty"}), 400

    # Check if sourcedir already exists for this language
    if (
        Sourcedir.select()
        .where(
            Sourcedir.path == path,
            Sourcedir.target_language_code == target_language_code,
        )
        .exists()
    ):
        return jsonify({"error": "Directory already exists"}), 409

    # Check if a sourcedir with the same slug exists for this language
    test_slug = slugify(str(path))
    if (
        Sourcedir.select()
        .where(
            Sourcedir.slug == test_slug,
            Sourcedir.target_language_code == target_language_code,
        )
        .exists()
    ):
        return jsonify({"error": "Directory already exists"}), 409

    try:
        # Create new sourcedir with language code
        sourcedir = Sourcedir.create(
            path=path,
            target_language_code=target_language_code,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        return (
            jsonify(
                {"id": sourcedir.id, "path": sourcedir.path, "slug": sourcedir.slug}
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>", methods=["DELETE"])
@api_auth_required
def delete_sourcedir_api(target_language_code: str, sourcedir_slug: str):
    """Delete a source directory if it's empty."""
    try:
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.target_language_code == target_language_code,
        )

        # Check if the sourcedir has any sourcefiles
        if Sourcefile.select().where(Sourcefile.sourcedir == sourcedir_entry).exists():
            return (
                jsonify({"error": "Cannot delete directory that contains files"}),
                400,
            )

        # Delete the sourcedir
        sourcedir_entry.delete_instance()
        return "", 204

    except DoesNotExist:
        return jsonify({"error": "Directory not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/language", methods=["PUT"]
)
@api_auth_required
def update_sourcedir_language_api(target_language_code: str, sourcedir_slug: str):
    """Update the language of a source directory."""
    try:
        data = request.get_json()
        if not data or "target_language_code" not in data:
            return (
                jsonify({"error": "Missing target_language_code parameter"}),
                400,
            )

        new_target_language_code = data["target_language_code"]

        # Validate the new language code
        if not new_target_language_code in VALID_target_language_codeS:
            return jsonify({"error": "Invalid language code"}), 400

        # Get the sourcedir entry
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.target_language_code == target_language_code,
        )

        # Check if a sourcedir with the same path already exists for the new language
        if (
            Sourcedir.select()
            .where(
                Sourcedir.path == sourcedir_entry.path,
                Sourcedir.target_language_code == new_target_language_code,
                Sourcedir.id != sourcedir_entry.id,  # type: ignore
            )
            .exists()
        ):
            return (
                jsonify({"error": "Directory already exists for the target language"}),
                409,
            )

        # Update the language code
        sourcedir_entry.target_language_code = new_target_language_code
        sourcedir_entry.save()

        return "", 204

    except DoesNotExist:
        return jsonify({"error": "Directory not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/rename", methods=["PUT"]
)
@api_auth_required
def rename_sourcedir_api(target_language_code: str, sourcedir_slug: str):
    """Rename a source directory."""
    try:
        data = request.get_json()
        if not data or "new_name" not in data:
            return jsonify({"error": "Missing new_name parameter"}), 400

        new_name = data["new_name"].strip()
        if not new_name:
            return jsonify({"error": "Invalid directory name"}), 400

        # Get the sourcedir entry
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.target_language_code == target_language_code,
        )

        # Check if a sourcedir with the new name already exists for this language
        if (
            Sourcedir.select()
            .where(
                Sourcedir.path == new_name,
                Sourcedir.target_language_code == target_language_code,
                Sourcedir.id != sourcedir_entry.id,  # type: ignore
            )
            .exists()
        ):
            return jsonify({"error": "A directory with this name already exists"}), 409

        # Update both path and slug
        sourcedir_entry.path = new_name
        sourcedir_entry.slug = slugify(new_name)
        sourcedir_entry.save()

        return jsonify({"new_name": new_name, "slug": sourcedir_entry.slug}), 200

    except DoesNotExist:
        return jsonify({"error": "Directory not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/upload", methods=["POST"]
)
@api_auth_required
def upload_sourcedir_new_sourcefile_api(target_language_code: str, sourcedir_slug: str):
    """Handle file upload to a source directory."""
    try:
        # Get the sourcedir entry by slug
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Check if files were uploaded
        if "files[]" not in request.files:
            flash("No files selected")
            return redirect(request.referrer)

        files = request.files.getlist("files[]")

        # Check number of files
        if len(files) > MAX_NUMBER_UPLOAD_FILES:
            flash(f"Too many files. Maximum {MAX_NUMBER_UPLOAD_FILES} files allowed")
            return redirect(request.referrer)

        # Get sourcedir using helper
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        uploaded_count = 0
        skipped_count = 0
        for file in files:
            if file.filename == "" or not file.filename:
                continue

            # Validate file
            if not allowed_file(file.filename):
                flash(
                    f'Invalid file type for {file.filename}. Supported formats: {", ".join(SOURCE_EXTENSIONS)}'
                )
                continue

            # Read file content
            file_content = file.read()

            # Check file size against upload limit
            if file.filename.endswith(".mp3"):
                size_limit = MAX_AUDIO_SIZE_UPLOAD_ALLOWED
            elif any(file.filename.endswith(ext) for ext in TEXT_SOURCE_EXTENSIONS):
                size_limit = MAX_TEXT_SIZE_UPLOAD_ALLOWED
            else:
                size_limit = MAX_IMAGE_SIZE_UPLOAD_ALLOWED

            if len(file_content) > size_limit:
                flash(
                    f"File {file.filename} too large (max {size_limit // (1024*1024)}MB)"
                )
                continue

            try:
                # Process the uploaded file
                print(f"\nDEBUG: Processing file {file.filename}")
                file_content, filename, metadata = process_uploaded_file(
                    file_content,
                    file.filename,
                    str(sourcedir_entry.path),
                    target_language_code,
                )
                print(f"DEBUG: Generated filename: {filename}")

                # Check if file already exists
                if (
                    Sourcefile.select()
                    .where(
                        (Sourcefile.sourcedir == sourcedir_entry)
                        & (Sourcefile.filename == filename)
                    )
                    .exists()
                ):
                    print(f"DEBUG: File {filename} already exists, skipping")
                    skipped_count += 1
                    continue

                # Create sourcefile entry without processing
                print(f"DEBUG: Creating sourcefile with filename {filename}")

                # Determine file type and set appropriate fields
                # Initialize description variable for all file types
                description = None
                if "description" in metadata and metadata["description"] is not None:
                    description = metadata["description"]

                if filename.endswith(".mp3"):
                    sourcefile_type = "audio"
                    image_data = None
                    audio_data = file_content
                    text_target = ""  # Will be populated during processing
                elif any(filename.endswith(ext) for ext in TEXT_SOURCE_EXTENSIONS):
                    sourcefile_type = "text"
                    image_data = None
                    audio_data = None
                    # For text files, we use the file content directly as text_target
                    text_target = file_content.decode("utf-8").strip()
                else:
                    sourcefile_type = "image"
                    image_data = file_content
                    audio_data = None
                    text_target = ""  # Will be populated during processing

                sourcefile = Sourcefile.create(
                    sourcedir=sourcedir_entry,
                    filename=filename,
                    image_data=image_data,
                    audio_data=audio_data,
                    text_target=text_target,
                    text_english="",  # Will be populated during processing
                    metadata=metadata,
                    sourcefile_type=sourcefile_type,
                    description=description,
                )
                print(f"DEBUG: Created sourcefile with ID {sourcefile.id}")
                uploaded_count += 1

            except ValueError as e:
                print(f"Upload validation error: {str(e)}")
                continue

        # Return JSON response with appropriate status code
        response_data = {
            "uploaded_count": uploaded_count,
            "skipped_count": skipped_count,
        }

        # Use HTTP 200 if files were uploaded, 204 if only skipped files,
        # or 400 if no valid files were uploaded
        if uploaded_count > 0:
            return jsonify(response_data), 200
        elif skipped_count > 0:
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "No valid files were uploaded"}), 400

    except DoesNotExist:
        return jsonify({"error": "Source directory not found"}), 404
    except Exception as e:
        print(f"DEBUG: Upload failed: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@sourcedir_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/update_description",
    methods=["PUT"],
)
@api_auth_required
def update_sourcedir_description_api(target_language_code: str, sourcedir_slug: str):
    """Update the description of a sourcedir."""
    try:
        # Get the data from the request
        data = request.get_json()
        if not data or "description" not in data:
            return jsonify({"error": "Missing description parameter"}), 400

        description = data["description"]

        # Get the sourcedir entry
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.target_language_code == target_language_code,
        )

        # Update the description
        sourcedir_entry.description = description
        sourcedir_entry.save()

        return "", 204  # No content response on success

    except DoesNotExist:
        return jsonify({"error": "Sourcedir not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route("/<target_language_code>/sources", methods=["GET"])
def get_sourcedirs_for_language_api(target_language_code: str):
    """Get all source directories for a specific language.

    Returns a JSON response with the sourcedirs and related statistics.
    """
    # Get sort parameter from query string (default to 'alpha')
    sort_by = request.args.get("sort", "date")

    try:
        # Use the utility function to get all data
        result = get_sourcedirs_for_language(target_language_code, sort_by)

        # Format the response for the API
        response = {
            "target_language_code": result["target_language_code"],
            "language_name": result["target_language_name"],
            "sources": [],
        }

        # Format sources in the expected structure for SvelteKit
        for sourcedir in result["sourcedirs"]:
            stats = result["sourcedir_stats"].get(sourcedir["slug"], {})
            source = {
                "name": sourcedir["path"],
                "display_name": sourcedir["path"],
                "slug": sourcedir["slug"],
                "description": sourcedir.get("description", ""),
                "created_at": (
                    sourcedir.get("created_at").isoformat()
                    if sourcedir.get("created_at")
                    else None
                ),
                "updated_at": (
                    sourcedir.get("updated_at").isoformat()
                    if sourcedir.get("updated_at")
                    else None
                ),
                "statistics": {
                    "file_count": stats.get("file_count", 0),
                    "sentence_count": stats.get("phrase_count", 0),
                },
                "is_empty": sourcedir["slug"] in result["empty_sourcedirs"],
            }
            response["sources"].append(source)

        # Return the formatted data
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting sourcedirs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcedir_api_bp.route("/<target_language_code>/<sourcedir_slug>", methods=["GET"])
def sourcefiles_for_sourcedir_api(target_language_code: str, sourcedir_slug: str):
    """
    Get all source files in a directory.

    Returns a JSON response with the sourcedir info and its sourcefiles.
    """
    try:
        # Use the utility function to get all data
        result = get_sourcefiles_for_sourcedir(target_language_code, sourcedir_slug)

        # Format the response for the API
        sourcedir_entry = result["sourcedir"]
        response = {
            "success": True,
            "sourcedir": {
                "id": sourcedir_entry.id,
                "path": sourcedir_entry.path,
                "slug": sourcedir_entry.slug,
                "description": sourcedir_entry.description,
                "target_language_code": sourcedir_entry.target_language_code,
                "created_at": (
                    sourcedir_entry.created_at.isoformat()
                    if sourcedir_entry.created_at
                    else None
                ),
                "updated_at": (
                    sourcedir_entry.updated_at.isoformat()
                    if sourcedir_entry.updated_at
                    else None
                ),
            },
            "sourcefiles": result["sourcefiles"],
            "language_name": result["target_language_name"],
            "has_vocabulary": result["has_vocabulary"],
            "supported_languages": result["supported_languages"],
        }

        return jsonify(response)

    except DoesNotExist:
        return jsonify({"success": False, "error": "Source directory not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving sourcefiles: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
