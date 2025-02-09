from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    jsonify,
    url_for,
)
from peewee import fn, DoesNotExist
import datetime
from slugify import slugify

from utils.lang_utils import get_language_name, get_all_languages, VALID_LANGUAGE_CODES
from db_models import (
    Sourcedir,
    Sourcefile,
    SourcefilePhrase,
)
from utils.sourcedir_utils import (
    _get_sourcedir_entry,
    allowed_file,
)
from utils.sourcefile_processing import process_uploaded_file
from config import (
    MAX_AUDIO_SIZE_UPLOAD_ALLOWED,
    MAX_IMAGE_SIZE_UPLOAD_ALLOWED,
    MAX_NUMBER_UPLOAD_FILES,
    SOURCE_EXTENSIONS,
)

sourcedir_views_bp = Blueprint("sourcedir_views", __name__)


@sourcedir_views_bp.route("/<target_language_code>/")
def sourcedirs_for_language(target_language_code: str):
    """Display all source directories."""
    sort_by = request.args.get("sort", "date")  # Default to recently modified
    target_language_name = get_language_name(target_language_code)

    # Get supported languages for the dropdown
    supported_languages = get_all_languages()

    # Query sourcedirs from database - filtered by language
    query = Sourcedir.select().where(Sourcedir.language_code == target_language_code)

    if sort_by == "date":
        # Sort by modification time, newest first
        query = query.order_by(
            fn.COALESCE(Sourcedir.updated_at, Sourcedir.created_at).desc()
        )
    else:
        # Default alphabetical sort
        query = query.order_by(Sourcedir.path)

    # Get all sourcedirs and check which ones are empty
    sourcedirs = []
    empty_sourcedirs = []
    sourcedir_stats = {}
    for sourcedir in query:
        sourcedirs.append({"path": sourcedir.path, "slug": sourcedir.slug})

        # Count sourcefiles
        sourcefile_count = (
            Sourcefile.select().where(Sourcefile.sourcedir == sourcedir).count()
        )
        if sourcefile_count == 0:
            empty_sourcedirs.append(sourcedir.slug)

        # Count phrases
        phrase_count = (
            SourcefilePhrase.select()
            .join(Sourcefile)
            .where(Sourcefile.sourcedir == sourcedir)
            .count()
        )

        sourcedir_stats[sourcedir.slug] = {
            "phrase_count": phrase_count,
            "path": sourcedir.path,
        }

    return render_template(
        "sourcedirs.jinja",
        target_language_code=target_language_code,
        target_language_name=target_language_name,
        sourcedirs=sourcedirs,
        empty_sourcedirs=empty_sourcedirs,
        current_sort=sort_by,
        supported_languages=supported_languages,
        sourcedir_stats=sourcedir_stats,
    )


@sourcedir_views_bp.route("/<target_language_code>/<sourcedir_slug>")
def sourcefiles_for_sourcedir(target_language_code: str, sourcedir_slug: str):
    """Display all source files in a directory."""
    target_language_name = get_language_name(target_language_code)

    # Get supported languages for the dropdown
    supported_languages = get_all_languages()

    try:
        # Get the sourcedir entry by slug
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Get all sourcefiles for this directory
        sourcefiles = []
        for sourcefile_entry in (
            Sourcefile.select()
            .where(Sourcefile.sourcedir == sourcedir_entry)
            .order_by(Sourcefile.filename)
        ):
            # Count wordforms and phrases
            wordform_count = sourcefile_entry.wordform_entries.count()
            phrase_count = sourcefile_entry.phrase_entries.count()

            # Prepare metadata for each file
            metadata = {
                "created_at": sourcefile_entry.created_at,
                "updated_at": sourcefile_entry.updated_at,
                "has_audio": sourcefile_entry.audio_data is not None,
                "wordform_count": wordform_count,
                "phrase_count": phrase_count,
            }
            if sourcefile_entry.metadata:
                if "image_processing" in sourcefile_entry.metadata:
                    metadata["image_processing"] = sourcefile_entry.metadata[
                        "image_processing"
                    ]
                if "duration" in sourcefile_entry.metadata:
                    metadata["duration"] = sourcefile_entry.metadata["duration"]
                if "video_title" in sourcefile_entry.metadata:
                    metadata["video_title"] = sourcefile_entry.metadata["video_title"]

            sourcefiles.append(
                {
                    "filename": sourcefile_entry.filename,
                    "slug": sourcefile_entry.slug,
                    "sourcefile_type": sourcefile_entry.sourcefile_type,
                    "metadata": metadata,
                }
            )

        # Check if any sourcefile has vocabulary
        has_vocabulary = any(sf["metadata"]["wordform_count"] > 0 for sf in sourcefiles)

        return render_template(
            "sourcefiles.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sourcedir_path=sourcedir_entry.path,  # Use path for display
            sourcedir_slug=sourcedir_slug,  # Use slug for URL generation
            sourcefiles=sourcefiles,
            supported_languages=supported_languages,
            has_vocabulary=has_vocabulary,
        )
    except DoesNotExist:
        # Return empty JSON array for nonexistent directories
        return "[]", 200, {"Content-Type": "application/json"}


@sourcedir_views_bp.route("/api/sourcedir/<target_language_code>", methods=["POST"])
def create_sourcedir(target_language_code: str):
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
            Sourcedir.language_code == target_language_code,
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
            Sourcedir.language_code == target_language_code,
        )
        .exists()
    ):
        return jsonify({"error": "Directory already exists"}), 409

    try:
        # Create new sourcedir with language code
        sourcedir = Sourcedir.create(
            path=path,
            language_code=target_language_code,
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


@sourcedir_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>", methods=["DELETE"]
)
def delete_sourcedir(target_language_code: str, sourcedir_slug: str):
    """Delete a source directory if it's empty."""
    try:
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.language_code == target_language_code,
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


@sourcedir_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/language", methods=["PUT"]
)
def update_sourcedir_language(target_language_code: str, sourcedir_slug: str):
    """Update the language of a source directory."""
    try:
        data = request.get_json()
        if not data or "language_code" not in data:
            return jsonify({"error": "Missing language_code parameter"}), 400

        new_language_code = data["language_code"]

        # Validate the new language code
        if not new_language_code in VALID_LANGUAGE_CODES:
            return jsonify({"error": "Invalid language code"}), 400

        # Get the sourcedir entry
        sourcedir_entry = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.language_code == target_language_code,
        )

        # Check if a sourcedir with the same path already exists for the new language
        if (
            Sourcedir.select()
            .where(
                Sourcedir.path == sourcedir_entry.path,
                Sourcedir.language_code == new_language_code,
                Sourcedir.id != sourcedir_entry.id,  # type: ignore
            )
            .exists()
        ):
            return (
                jsonify({"error": "Directory already exists for the target language"}),
                409,
            )

        # Update the language code
        sourcedir_entry.language_code = new_language_code
        sourcedir_entry.save()

        return "", 204

    except DoesNotExist:
        return jsonify({"error": "Directory not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcedir_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/rename", methods=["PUT"]
)
def rename_sourcedir(target_language_code: str, sourcedir_slug: str):
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
            Sourcedir.language_code == target_language_code,
        )

        # Check if a sourcedir with the new name already exists for this language
        if (
            Sourcedir.select()
            .where(
                Sourcedir.path == new_name,
                Sourcedir.language_code == target_language_code,
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


@sourcedir_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/upload", methods=["POST"]
)
def upload_sourcedir_new_sourcefile(target_language_code: str, sourcedir_slug: str):
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
            size_limit = (
                MAX_AUDIO_SIZE_UPLOAD_ALLOWED
                if file.filename.endswith(".mp3")
                else MAX_IMAGE_SIZE_UPLOAD_ALLOWED
            )
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
                sourcefile = Sourcefile.create(
                    sourcedir=sourcedir_entry,
                    filename=filename,
                    image_data=None if filename.endswith(".mp3") else file_content,
                    audio_data=file_content if filename.endswith(".mp3") else None,
                    text_target="",  # Will be populated during processing
                    text_english="",  # Will be populated during processing
                    metadata=metadata,
                    sourcefile_type=(
                        "audio" if filename.endswith(".mp3") else "image"
                    ),  # Set type based on extension
                )
                print(f"DEBUG: Created sourcefile with ID {sourcefile.id}")
                uploaded_count += 1

            except ValueError as e:
                flash(str(e))
                continue

        # Show appropriate messages for uploaded and skipped files
        if uploaded_count > 0:
            if uploaded_count == 1:
                flash(f"Successfully uploaded {uploaded_count} file")
            else:
                flash(f"Successfully uploaded {uploaded_count} files")
        if skipped_count > 0:
            if skipped_count == 1:
                flash(f"Skipped {skipped_count} existing file")
            else:
                flash(f"Skipped {skipped_count} existing files")
        if uploaded_count == 0 and skipped_count == 0:
            flash("No valid files were uploaded")

        return redirect(
            url_for(
                "sourcedir_views.sourcefiles_for_sourcedir",
                target_language_code=target_language_code,
                sourcedir_slug=sourcedir_slug,
            )
        )

    except DoesNotExist:
        flash("Source directory not found")
        return redirect(request.referrer)
    except Exception as e:
        flash(f"Upload failed: {str(e)}")
        return redirect(request.referrer)
