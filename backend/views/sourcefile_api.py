"""API endpoints for sourcefiles.

All endpoints for interacting with sourcefiles programmatically.
These endpoints follow the standard pattern:
/api/lang/sourcefile/...
"""

import os
import json
import tempfile
import random
import time
from datetime import datetime
from pathlib import Path
import uuid

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    g,
    url_for,
)
from peewee import DoesNotExist

from utils.env_config import ELEVENLABS_API_KEY
from utils.audio_utils import add_delays, ensure_model_audio_data
from config import (
    MAX_AUDIO_SIZE_FOR_STORAGE,
    DEFAULT_LANGUAGE_LEVEL,
    DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING,
    DEFAULT_MAX_NEW_WORDS_PER_PROCESSING,
)
from db_models import (
    Lemma,
    Sourcedir,
    Sourcefile,
    Sentence,
    SentenceLemma,
)
from gjdutils.outloud_text_to_speech import outloud_elevenlabs
from utils.sourcedir_utils import (
    _get_sourcedir_entry,
    get_sourcedir_or_404,
    get_sourcedirs_for_language,
)
from utils.sourcefile_utils import (
    _get_sourcefile_entry,
    get_sourcefile_details,
    process_sourcefile,
    _create_text_sourcefile,
    preprocess_html_for_llm,
)
from utils.store_utils import load_or_generate_lemma_metadata
from utils.youtube_utils import YouTubeDownloadError, download_audio
from slugify import slugify
from utils.types import LanguageLevel
from typing import get_args
import requests
from utils.vocab_llm_utils import extract_text_from_html
from utils.lang_utils import get_language_name
from utils.auth_utils import api_auth_required
from utils.url_registry import endpoint_for
from utils.lang_utils import validate_language_level
import utils.generate_sourcefiles as gen_sf
from views.sourcefile_views import inspect_sourcefile_text_vw

# Create a blueprint with standardized prefix
sourcefile_api_bp = Blueprint(
    "sourcefile_api", __name__, url_prefix="/api/lang/sourcefile"
)


def _inspect_sourcefile_core(
    target_language_code: str,
    sourcedir_slug: str,
    sourcefile_slug: str,
    purpose: str,
):
    """Core implementation for all sourcefile inspection API endpoints.

    Args:
        target_language_code: The language code
        sourcedir_slug: The sourcedir slug
        sourcefile_slug: The sourcefile slug
        purpose: The purpose of the request ("basic", "text", "words", "phrases", or "translation")

    Returns:
        JSON response with data specific to the requested purpose
    """
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Use the shared utility function to get details with the specified purpose
        details = get_sourcefile_details(
            sourcefile_entry, target_language_code, purpose=purpose
        )

        # Create a response with the details
        response_data = {
            "success": True,
            "sourcefile": details["sourcefile"],
            "sourcedir": details["sourcedir"],
            "metadata": details["metadata"],
            "navigation": details["navigation"],
            "stats": details["stats"],
        }

        # Get available sourcedirs for this language (for the dropdown)
        # Use the utility function to get sourcedirs
        sourcedirs_result = get_sourcedirs_for_language(target_language_code, "date")

        # Format sources in the expected structure for SvelteKit
        available_sourcedirs = []
        for sourcedir in sourcedirs_result["sourcedirs"]:
            # Skip the current sourcedir
            if sourcedir["slug"] == sourcedir_slug:
                continue

            stats = sourcedirs_result["sourcedir_stats"].get(sourcedir["slug"], {})
            source = {
                "name": sourcedir["path"],
                "display_name": sourcedir["path"],
                "slug": sourcedir["slug"],
                "description": sourcedir.get("description", ""),
                "statistics": {
                    "file_count": stats.get("file_count", 0),
                    "sentence_count": stats.get("phrase_count", 0),
                },
                "is_empty": sourcedir["slug"] in sourcedirs_result["empty_sourcedirs"],
            }
            available_sourcedirs.append(source)

        response_data["available_sourcedirs"] = available_sourcedirs

        # Include recognized_words/text_data at the top-level for clients that expect it
        if "recognized_words" in details:
            response_data["recognized_words"] = details["recognized_words"]
        if "text_data" in details:
            response_data["text_data"] = details["text_data"]

        # Add purpose-specific data
        if purpose == "text" and "enhanced_text" in details:
            response_data["enhanced_text"] = details["enhanced_text"]
            response_data["wordforms"] = details.get("wordforms", [])
            # Also add enhanced_text to the sourcefile object for backwards compatibility
            # This is where the frontend component expects to find it
            response_data["sourcefile"]["enhanced_text"] = details["enhanced_text"]
        elif purpose == "words" and "wordforms" in details:
            response_data["wordforms"] = details["wordforms"]
        elif purpose == "phrases" and "phrases" in details:
            response_data["phrases"] = details["phrases"]
        elif purpose == "translation":
            # For translation tab, ensure text content is included
            # (this is already handled in get_sourcefile_details)
            pass

        return jsonify(response_data)

    except DoesNotExist:
        return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        # Log the full traceback
        current_app.logger.exception(
            f"Error in inspect_sourcefile_{purpose}_api for {target_language_code}/{sourcedir_slug}/{sourcefile_slug}"
        )
        # Return 500 with the error message (as before)
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>", methods=["GET"]
)
def inspect_sourcefile_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get basic info about a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "basic"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/text",
    methods=["GET"],
)
def inspect_sourcefile_text_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the text content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "text"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/words",
    methods=["GET"],
)
def inspect_sourcefile_words_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the words content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "words"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/phrases",
    methods=["GET"],
)
def inspect_sourcefile_phrases_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the phrases content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "phrases"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/translation",
    methods=["GET"],
)
def inspect_sourcefile_translation_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the translation content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "translation"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/image",
    methods=["GET"],
)
def inspect_sourcefile_image_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the image tab content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "image"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/audio",
    methods=["GET"],
)
def inspect_sourcefile_audio_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """API endpoint to get the audio tab content of a sourcefile."""
    return _inspect_sourcefile_core(
        target_language_code, sourcedir_slug, sourcefile_slug, "audio"
    )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process",
    methods=["POST"],
)
@api_auth_required
def process_sourcefile_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process a source file to transcribe, translate, and extract wordforms and phrases.
    This is now a synchronous operation - the request will complete after all processing is done.
    """
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get processing parameters from request or use defaults
        data = request.get_json() or {}

        def already_processed(sourcefile_entry: Sourcefile):
            return bool(sourcefile_entry.text_target)

        # Get parameters from request or use defaults
        if "max_new_words" in data:
            max_new_words = int(data["max_new_words"])
        else:
            max_new_words = DEFAULT_MAX_NEW_WORDS_PER_PROCESSING

        if "max_new_phrases" in data:
            max_new_phrases = int(data["max_new_phrases"])
        else:
            max_new_phrases = DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING

        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)
        assert language_level in get_args(
            LanguageLevel
        ), f"Invalid language level: {language_level}"

        # Process the sourcefile synchronously
        process_sourcefile(
            sourcefile_entry,
            language_level=language_level,  # type: ignore
            max_new_words=max_new_words,
            max_new_phrases=max_new_phrases,
        )

        # Return success response
        return jsonify(
            {
                "success": True,
                "message": "Sourcefile processing completed",
                "params": {
                    "max_new_words": max_new_words,
                    "max_new_phrases": max_new_phrases,
                    "language_level": language_level,
                },
            }
        )

    except DoesNotExist:
        return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error processing sourcefile: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


def _process_individual_lemma(lemma: str, target_language_code: str):
    """Process a single lemma, generating metadata and audio for its sentences.

    Includes random jitter to avoid overwhelming external APIs."""
    # Add jitter delay between 0 and 2 seconds
    time.sleep(random.uniform(0, 2))

    try:
        _ = load_or_generate_lemma_metadata(
            lemma, target_language_code, generate_if_incomplete=True
        )

        # Get example sentences
        sentences = (
            Sentence.select()
            .join(SentenceLemma)
            .join(Lemma)
            .where(Lemma.lemma == lemma)
        )

        # Generate audio for each sentence
        for sentence in sentences:
            ensure_model_audio_data(sentence, should_add_delays=True, verbose=1)

    except Exception as e:
        print(f"Error processing lemma {lemma}: {str(e)}")
        raise


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_individual",
    methods=["POST"],
)
@api_auth_required
def process_individual_words_api(target_language_code, sourcedir_slug, sourcefile_slug):
    """Process individual words in a sourcefile, generating full metadata and audio."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get all wordforms for this sourcefile
        wordforms = [sw.wordform for sw in sourcefile_entry.wordform_entries]  # type: ignore

        # Get unique lemmas through the lemma_entry relationship
        unique_lemmas = {wf.lemma_entry.lemma for wf in wordforms}

        # Track processed and failed lemmas
        processed_lemmas = []
        failed_lemmas = []

        # Process lemmas serially with a standard for loop
        for lemma in unique_lemmas:
            try:
                _process_individual_lemma(lemma, target_language_code)
                processed_lemmas.append(lemma)
            except Exception as e:
                failed_lemmas.append({"lemma": lemma, "error": str(e)})
                print(f"Failed to process lemma {lemma}: {str(e)}")
                # Continue processing other lemmas even if one fails

        print(f"Done processing sourcefile {sourcefile_slug}")

        # Return information about what was processed
        return "", 204
    except Exception as e:
        response = jsonify({"success": False, "error": str(e)})
        response.status_code = 500
        return response


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/update_description",
    methods=["PUT"],
)
@api_auth_required
def update_sourcefile_description_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Update the description of a sourcefile."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get and validate the description from the request
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Missing request data"}), 400

        description = data.get("description", "").strip()

        # Update the description
        setattr(sourcefile_entry, "description", description if description else None)
        sourcefile_entry.save()

        return "", 204  # No content, success

    except DoesNotExist:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating description: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/move",
    methods=["PUT"],
)
@api_auth_required
def move_sourcefile_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Move a sourcefile to a different sourcedir."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get and validate the new sourcedir from the request
        data = request.get_json()
        if data is None or "new_sourcedir_slug" not in data:
            return jsonify({"error": "Missing new_sourcedir_slug parameter"}), 400

        new_sourcedir_slug = data.get("new_sourcedir_slug").strip()
        if not new_sourcedir_slug:
            return jsonify({"error": "Invalid sourcedir slug"}), 400

        # Get the new sourcedir entry
        try:
            new_sourcedir_entry = Sourcedir.get(
                Sourcedir.slug == new_sourcedir_slug,
                Sourcedir.target_language_code == target_language_code,
            )
        except DoesNotExist:
            return jsonify({"error": "Target directory not found"}), 404

        # Don't do anything if it's the same sourcedir
        if sourcefile_entry.sourcedir.id == new_sourcedir_entry.id:
            return jsonify({"message": "File is already in this directory"}), 200

        # Check if a file with the same filename already exists in the new sourcedir
        if (
            Sourcefile.select()
            .where(
                (Sourcefile.sourcedir == new_sourcedir_entry)
                & (Sourcefile.filename == sourcefile_entry.filename)
            )
            .exists()
        ):
            return (
                jsonify(
                    {
                        "error": "A file with this name already exists in the target directory"
                    }
                ),
                409,
            )

        # Update the sourcedir
        sourcefile_entry.sourcedir = new_sourcedir_entry
        sourcefile_entry.save()  # This will also update the slug if needed

        return (
            jsonify(
                {
                    "message": "File moved successfully",
                    "new_sourcedir_slug": new_sourcedir_slug,
                    "new_sourcefile_slug": sourcefile_entry.slug,
                }
            ),
            200,
        )

    except DoesNotExist:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error moving sourcefile: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>",
    methods=["DELETE"],
)
@api_auth_required
def delete_sourcefile_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Delete a source file."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Log deletion attempt
        current_app.logger.info(
            f"Attempting to delete sourcefile: {sourcefile_entry.filename} "
            f"(ID: {sourcefile_entry.id}) from sourcedir: {sourcedir_slug}"  # type: ignore
        )

        try:
            # Delete the sourcefile - related records will be deleted automatically
            # due to ON DELETE CASCADE constraints
            sourcefile_entry.delete_instance()
            current_app.logger.info(
                f"Successfully deleted sourcefile: {sourcefile_entry.filename}"
            )
            return "", 204
        except Exception as e:
            current_app.logger.error(
                f"Error deleting sourcefile {sourcefile_entry.filename}: {str(e)}",
                exc_info=True,
            )
            return (
                jsonify(
                    {
                        "error": f"Failed to delete file: {str(e)}",
                        "details": {
                            "filename": sourcefile_entry.filename,
                            "id": sourcefile_entry.id,  # type: ignore
                            "sourcedir": sourcedir_slug,
                        },
                    }
                ),
                500,
            )

    except DoesNotExist:
        current_app.logger.warning(
            f"Attempted to delete non-existent sourcefile: {sourcefile_slug} "
            f"from sourcedir: {sourcedir_slug}"
        )
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        current_app.logger.error(
            f"Unexpected error in delete_sourcefile: {str(e)}", exc_info=True
        )
        return (
            jsonify(
                {
                    "error": f"Unexpected error: {str(e)}",
                    "details": {
                        "sourcefile_slug": sourcefile_slug,
                        "sourcedir_slug": sourcedir_slug,
                    },
                }
            ),
            500,
        )


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/rename",
    methods=["PUT"],
)
@api_auth_required
def rename_sourcefile_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Rename a source file."""
    try:
        data = request.get_json()
        if not data or "new_name" not in data:
            return jsonify({"error": "Missing new_name parameter"}), 400

        new_name = data["new_name"].strip()
        if not new_name:
            return jsonify({"error": "Invalid filename"}), 400

        # Get the sourcefile entry first so we can check the original extension
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Keep the original extension
        old_ext = Path(str(sourcefile_entry.filename)).suffix
        new_ext = Path(new_name).suffix
        if not new_ext:
            new_name = new_name + old_ext
        elif new_ext.lower() != old_ext.lower():
            return jsonify({"error": "File extension cannot be changed"}), 400

        # Get the sourcedir entry
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Check if a file with the new name already exists
        if (
            Sourcefile.select()
            .where(
                (Sourcefile.sourcedir == sourcedir_entry)
                & (Sourcefile.filename == new_name)
            )
            .exists()
        ):
            return jsonify({"error": "A file with this name already exists"}), 409

        # Update the filename - this will trigger slug regeneration in save()
        sourcefile_entry.filename = new_name  # type: ignore
        sourcefile_entry.save()

        return jsonify({"new_name": new_name, "new_slug": sourcefile_entry.slug}), 200

    except DoesNotExist:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/create_from_text",
    methods=["POST"],
)
@api_auth_required
def create_sourcefile_from_text_api(target_language_code: str, sourcedir_slug: str):
    """Create a new sourcefile from pasted text."""
    try:
        # Get the sourcedir entry by slug
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Get and validate parameters
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title", "").strip()
        text_target = data.get("text_target", "").strip()
        description = data.get("description")
        language_level = data.get("language_level")
        if description is not None:
            description = description.strip() or None

        if not title:
            return jsonify({"error": "Title is required"}), 400
        if not text_target:
            return jsonify({"error": "Text content is required"}), 400

        # Prepare data for helper function - slugify the title for filename
        from slugify import slugify as _slugify
        filename = f"{_slugify(title)}.txt"
        metadata = {"text_format": "plain"}

        # Use helper to create sourcefile (handles collision)
        try:
            sourcefile = _create_text_sourcefile(
                sourcedir_entry=sourcedir_entry,
                filename=filename,
                text_target=text_target,
                description=description,
                metadata=metadata,
                sourcefile_type="text",
                created_by_id=g.user["id"] if g.user else None,
                language_level=language_level,
            )
        except ValueError as e:  # Catch collision error from helper
            # Log the collision specifically
            current_app.logger.error(
                f"Filename collision error for {filename} in {sourcedir_slug}: {str(e)}"
            )
            return (
                jsonify(
                    {
                        "error": f"File {filename} already exists or could not create unique name."
                    }
                ),
                409,
            )

        return (
            jsonify(
                {
                    "message": "Successfully created file",
                    "filename": sourcefile.filename,  # Use filename from created object
                    "slug": sourcefile.slug,
                }
            ),
            200,
        )

    except DoesNotExist:
        return jsonify({"error": "Target directory not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in create_sourcefile_from_text: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/youtube",
    methods=["POST"],
)
@api_auth_required
def add_sourcefile_from_youtube_api(target_language_code, sourcedir_slug):
    """Add a new sourcefile from a YouTube video's audio."""
    sourcedir = get_sourcedir_or_404(target_language_code, sourcedir_slug)

    data = request.get_json()
    if not data or "youtube_url" not in data:
        return jsonify({"error": "YouTube URL is required"}), 400

    youtube_url = data["youtube_url"].strip()
    if not youtube_url:
        return jsonify({"error": "YouTube URL cannot be empty"}), 400

    try:
        # Download audio and get metadata
        audio_data, metadata = download_audio(youtube_url)

        # Create filename from video title and timestamp
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"{metadata['video_title']} [{timestamp}].mp3"

        # Check if file already exists
        if (
            Sourcefile.select()
            .where(
                Sourcefile.sourcedir == sourcedir,
                Sourcefile.filename == filename,
            )
            .exists()
        ):
            return jsonify({"error": f"File {filename} already exists"}), 409

        # Create new sourcefile
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir,
            filename=filename,
            sourcefile_type="youtube_audio",
            audio_data=audio_data,
            text_target="",  # Initialize with empty string
            text_english="",  # Initialize with empty string
            metadata=metadata,
        )

        return jsonify(
            {
                "filename": sourcefile.filename,
                "id": sourcefile.id,
                "slug": sourcefile.slug,
            }
        )

    except YouTubeDownloadError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        current_app.logger.error(f"Error downloading YouTube audio: {e}")
        return jsonify({"error": "Failed to download audio"}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/generate",
    methods=["POST"],
)
@api_auth_required
def generate_sourcefile_api(target_language_code: str):
    """Generate an AI Sourcefile for a language.

    Request JSON body (all optional):
      - title: Optional[str]
      - language_level: Optional[str] in {A1,A2,B1,B2,C1,C2}
      - sourcedir_path: Optional[str]

    Returns 200 JSON:
      { sourcedir_slug, sourcefile_slug, url_text_tab }
    """
    try:
        data = request.get_json() or {}

        # Validate/normalize inputs
        raw_title = data.get("title")
        title = raw_title.strip() if isinstance(raw_title, str) else None

        raw_level = data.get("language_level")
        if raw_level is not None:
            try:
                language_level = validate_language_level(str(raw_level))
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        else:
            language_level = None

        sourcedir_path_raw = data.get("sourcedir_path")
        sourcedir_path = (
            sourcedir_path_raw.strip() if isinstance(sourcedir_path_raw, str) else None
        ) or gen_sf.DEFAULT_SOURCEDIR_NAME

        # Choose level if not provided
        if language_level is None:
            language_level = gen_sf.choose_language_level(target_language_code)

        # Ensure sourcedir exists
        sourcedir_entry = gen_sf.get_or_create_ai_sourcedir(
            target_language_code, sourcedir_path
        )

        # Generate title if not provided
        if not title:
            title = gen_sf.generate_topic(
                target_language_code=target_language_code,
                sourcedir_path=sourcedir_path,
                language_level=language_level,
            )

        # Log start
        try:
            user_id = g.user.get("id") if g.user else None
        except Exception:
            user_id = None
        current_app.logger.info(
            f"[generate_sourcefile_api] user={user_id} lang={target_language_code} level={language_level} sourcedir='{sourcedir_path}' title='{title}'"
        )

        # Generate content
        generated_text, tags = gen_sf.generate_content(
            target_language_code=target_language_code,
            title=title,
            language_level=language_level,
            text_type=None,
        )

        # Prepare filename and metadata
        filename = f"{title}.txt"
        # Avoid filename collisions within the sourcedir
        if (
            Sourcefile.select()
            .where(
                Sourcefile.sourcedir == sourcedir_entry,
                Sourcefile.filename == filename,
            )
            .exists()
        ):
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            filename = f"{title} [{timestamp}].txt"

        description = "AI-generated by Claude Sonnet 4"
        tags_str = ";".join(tags or [])
        metadata = {
            "generated": True,
            "title": title,
            "language_level": language_level,
            "generation_method": "llm",
            "tags": tags_str,
            "model": "Claude Sonnet 4",
        }

        # Create Sourcefile
        # Validate created_by_id is a UUID if present; otherwise omit
        created_by_id: str | None = None
        if user_id:
            try:
                _ = uuid.UUID(str(user_id))
                created_by_id = str(user_id)
            except Exception:
                created_by_id = None

        sourcefile = _create_text_sourcefile(
            sourcedir_entry=sourcedir_entry,
            filename=filename,
            text_target=generated_text,
            description=description,
            metadata=metadata,
            sourcefile_type="text",
            created_by_id=created_by_id,
            language_level=language_level,
            ai_generated=True,
        )

        # Build redirect URL to Text tab
        url_text_tab = url_for(
            endpoint_for(inspect_sourcefile_text_vw),
            target_language_code=target_language_code,
            sourcedir_slug=sourcedir_entry.slug,
            sourcefile_slug=sourcefile.slug,
        )

        # Log completion
        current_app.logger.info(
            f"[generate_sourcefile_api] created file id={sourcefile.id} filename='{sourcefile.filename}' url='{url_text_tab}'"
        )

        return (
            jsonify(
                {
                    "sourcedir_slug": sourcedir_entry.slug,
                    "sourcefile_slug": sourcefile.slug,
                    "url_text_tab": url_text_tab,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error in generate_sourcefile_api: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate_audio",
    methods=["POST"],
)
@api_auth_required
def generate_sourcefile_audio_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Generate audio for a sourcefile using ElevenLabs."""
    temp_file = None
    try:
        sourcefile_entry = (
            Sourcefile.select()
            .join(Sourcedir)
            .where(
                (Sourcedir.target_language_code == target_language_code)
                & (Sourcedir.slug == sourcedir_slug)
                & (Sourcefile.slug == sourcefile_slug)
            )
            .get()
        )

        if not sourcefile_entry.text_target:
            return (
                jsonify({"error": "No text content available for audio generation"}),
                400,
            )

        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        try:
            outloud_elevenlabs(
                text=add_delays(str(sourcefile_entry.text_target)),
                api_key=ELEVENLABS_API_KEY.get_secret_value().strip(),
                mp3_filen=temp_file.name,
            )

            # Read the generated audio
            temp_file.seek(0)
            audio_data = temp_file.read()

            # Check size
            if len(audio_data) > MAX_AUDIO_SIZE_FOR_STORAGE:
                raise ValueError(
                    f"Generated audio too large (max {MAX_AUDIO_SIZE_FOR_STORAGE/(1024*1024):.1f}MB)"
                )

            # Store in database
            sourcefile_entry.audio_data = bytes(audio_data)  # Ensure it's bytes
            sourcefile_entry.save()

            return "", 204

        except Exception as e:
            current_app.logger.error(f"Error generating audio: {str(e)}")
            error_msg = str(e)
            if "API key" in error_msg:
                error_msg = "Invalid or missing API key"
            elif "quota" in error_msg.lower():
                error_msg = "API quota exceeded"
            return jsonify({"error": f"Failed to generate audio: {error_msg}"}), 500

    except DoesNotExist:
        return jsonify({"error": "Source file not found"}), 404

    finally:
        # Clean up temp file
        if temp_file is not None:
            try:
                temp_file.close()
                os.unlink(temp_file.name)
            except Exception as e:
                current_app.logger.error(f"Error cleaning up temp file: {str(e)}")


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/create_from_url",
    methods=["POST"],
)
@api_auth_required
def create_sourcefile_from_url_api(target_language_code: str, sourcedir_slug: str):
    """Create a new sourcefile by fetching and extracting text from a URL."""
    try:
        # Get the sourcedir entry by slug
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)
        # Get language name from the code, not the potentially unloaded relation
        try:
            target_language_name = get_language_name(target_language_code)
        except LookupError:
            return (
                jsonify(
                    {"error": f"Invalid target language code: {target_language_code}"}
                ),
                400,
            )

        # Get and validate parameters
        data = request.get_json()
        if not data or not data.get("url"):
            return jsonify({"error": "URL is required"}), 400

        url = data.get("url", "").strip()
        language_level = data.get("language_level")
        if not url:
            return jsonify({"error": "URL cannot be empty"}), 400

        # Fetch HTML content from URL
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            html_content = response.text
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to fetch URL {url} with UA: {str(e)}")
            return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 400
        except Exception as e:
            current_app.logger.error(f"Unexpected error fetching URL {url}: {str(e)}")
            return jsonify({"error": f"Error fetching URL: {str(e)}"}), 500

        # --- Pre-process HTML using utility function --- START ---
        try:
            simplified_html = preprocess_html_for_llm(html_content)
        except Exception as e:
            # Handle exceptions raised by the preprocessing function
            current_app.logger.error(
                f"HTML preprocessing failed for URL {url}: {str(e)}"
            )
            return jsonify({"error": f"Failed to process HTML content: {str(e)}"}), 500
        # --- Pre-process HTML using utility function --- END ---

        # Extract title and text using LLM, passing the simplified HTML
        try:
            extracted_title, extracted_text, _ = extract_text_from_html(
                html_content=simplified_html,  # Use simplified HTML
                target_language_name=target_language_name,
                verbose=1,  # Or adjust verbosity as needed
            )
            # Check if extracted text is meaningful
            if not extracted_text or extracted_text == "-":
                current_app.logger.warning(
                    f"LLM returned no meaningful text for {url}. Title: '{extracted_title}', Text: '{extracted_text}'"
                )
                return (
                    jsonify(
                        {"error": "Could not extract meaningful text from the URL."}
                    ),
                    400,
                )
        except Exception as e:
            current_app.logger.error(
                f"LLM text extraction failed for URL {url}: {str(e)}"
            )
            return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

        # ---- Filename Generation using Title ---- START ----
        # Generate filename from title, fallback to URL-based name
        if not extracted_title or extracted_title == "-":
            # Fallback if title is missing or unusable
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            sanitized_url_part = slugify(
                url.split("//")[-1].split("/")[0], max_length=50
            )
            # Use .txt for fallback as well
            filename = f"url_{sanitized_url_part}_{timestamp}.txt"
        else:
            # Use the extracted title directly, ensuring it ends with .txt
            filename = extracted_title
            if not filename.lower().endswith(".txt"):
                filename += ".txt"

        # Check for potential collision before calling helper (optional but safer)
        if (
            Sourcefile.select()
            .where(
                (Sourcefile.sourcedir == sourcedir_entry)
                & (Sourcefile.filename == filename)  # Check exact filename
            )
            .exists()
        ):
            # Collision handling: append timestamp to the original title-based filename
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )  # Use full year for clarity
            base, ext = os.path.splitext(filename)
            filename = f"{base} ({timestamp}){ext}"
        # ---- Filename Generation using Title ---- END ----

        # Prepare data for helper function
        metadata = {
            "text_format": "plain",
            "source_url": url,
            "extracted_title": extracted_title,
        }
        description = f"Title: {extracted_title}\nUploaded from URL: {url}"

        # Use helper to create sourcefile (collision check inside helper is removed)
        try:
            sourcefile = _create_text_sourcefile(
                sourcedir_entry=sourcedir_entry,
                filename=filename,  # Pass the determined filename
                text_target=extracted_text,  # Pass only the extracted text
                description=description,  # Pass updated description
                metadata=metadata,  # Pass updated metadata
                sourcefile_type="text",
                created_by_id=g.user["id"] if g.user else None,
                url=url,  # Pass the source URL
                language_level=language_level,  # Pass language_level
            )
        except (
            ValueError
        ) as e:  # Catch potential errors from helper (though collision is removed)
            current_app.logger.error(f"Error creating sourcefile for {url}: {str(e)}")
            return jsonify({"error": f"Could not create sourcefile entry."}), 500

        return (
            jsonify(
                {
                    "message": "Successfully created file from URL",
                    "filename": sourcefile.filename,  # Use filename from created object
                    "slug": sourcefile.slug,
                }
            ),
            200,
        )

    except DoesNotExist:
        return jsonify({"error": "Target directory not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error in create_sourcefile_from_url: {str(e)}")
        return jsonify({"error": str(e)}), 500
