import os
import json
import tempfile
from datetime import datetime
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from pathlib import Path
from peewee import DoesNotExist

from slugify import slugify
from utils.env_config import ELEVENLABS_API_KEY
from utils.audio_utils import add_delays, ensure_model_audio_data
from config import (
    LANGUAGE_LEVEL,
    MAX_AUDIO_SIZE_FOR_STORAGE,
)
from db_models import (
    Lemma,
    Phrase,
    Sourcedir,
    Sourcefile,
    SourcefilePhrase,
    SourcefileWordform,
    Wordform,
    Sentence,
    SentenceLemma,
    fn,
)
from gjdutils.outloud_text_to_speech import outloud_elevenlabs
from gjdutils.jsons import jsonify
from utils.lang_utils import get_language_name
from utils.sentence_utils import generate_practice_sentences, get_all_sentences
from utils.sourcedir_utils import (
    _get_navigation_info,
    _get_sourcedir_entry,
    _get_sourcefile_entry,
    _navigate_sourcefile,
    get_sourcedir_or_404,
)
from utils.sourcefile_processing import process_sourcefile_content
from utils.store_utils import load_or_generate_lemma_metadata
from utils.vocab_llm_utils import (
    create_interactive_word_links,
    extract_tricky_words_or_phrases,
    normalize_text,
)
from utils.youtube_utils import YouTubeDownloadError, download_audio
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import time
from utils.word_utils import get_sourcefile_lemmas

sourcefile_views_bp = Blueprint("sourcefile_views", __name__)


@sourcefile_views_bp.route("/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>")
def inspect_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Redirect to the text view of a source file."""
    try:
        # Check if the file exists first
        _get_sourcefile_entry(target_language_code, sourcedir_slug, sourcefile_slug)

        return redirect(
            url_for(
                "sourcefile_views.inspect_sourcefile_text",
                target_language_code=target_language_code,
                sourcedir_slug=sourcedir_slug,
                sourcefile_slug=sourcefile_slug,
            )
        )
    except DoesNotExist:
        abort(404, description="File not found")


# Helper functions for reducing redundancy in inspect_sourcefile_* views
def _get_wordforms_data(sourcefile_entry):
    """Get wordforms data using the optimized query, including junction table data in one query."""
    # Use the enhanced version of get_all_wordforms_for that includes junction data
    language_code = sourcefile_entry.sourcedir.language_code

    # This avoids N+1 queries by including junction table data in a single query
    return Wordform.get_all_wordforms_for(
        language_code=language_code,
        sourcefile=sourcefile_entry,
        include_junction_data=True,  # This will return wordform dicts with centrality and ordering
    )


def _get_phrases_data(sourcefile_entry):
    """Get phrases data using the optimized query with included junction data."""
    language_code = sourcefile_entry.sourcedir.language_code

    # Use the enhanced get_all_phrases_for method with include_junction_data=True
    # This returns phrase dictionaries with centrality and ordering already included
    return Phrase.get_all_phrases_for(
        language_code=language_code,
        sourcefile=sourcefile_entry,
        include_junction_data=True,  # This will return phrase dicts with centrality and ordering
    )


def _get_phrases_count(sourcefile_entry):
    """Get only the phrase count for a sourcefile."""
    return (
        SourcefilePhrase.select()
        .where(SourcefilePhrase.sourcefile == sourcefile_entry)
        .count()
    )


def _get_wordforms_count(sourcefile_entry):
    """Get only the wordforms count for a sourcefile."""
    return (
        SourcefileWordform.select()
        .where(SourcefileWordform.sourcefile == sourcefile_entry)
        .count()
    )


def _get_sourcefile_metadata(sourcefile_entry):
    """Create a metadata dictionary for a sourcefile."""
    metadata = {
        "created_at": sourcefile_entry.created_at,
        "updated_at": sourcefile_entry.updated_at,
    }
    if sourcefile_entry.metadata and "image_processing" in sourcefile_entry.metadata:
        metadata["image_processing"] = sourcefile_entry.metadata["image_processing"]

    return metadata


def _get_available_sourcedirs(target_language_code):
    """Get all available sourcedirs for a language."""
    return (
        Sourcedir.select(Sourcedir.path, Sourcedir.slug)
        .where(Sourcedir.language_code == target_language_code)
        .order_by(Sourcedir.path)
    )


def _get_common_template_params(
    target_language_code,
    target_language_name,
    sourcefile_entry,
    sourcedir_slug,
    sourcefile_slug,
    nav_info,
    metadata,
    already_processed,
    available_sourcedirs,
):
    """Get common template parameters used in all sourcefile view functions."""
    return {
        "target_language_code": target_language_code,
        "target_language_name": target_language_name,
        "sourcedir": sourcefile_entry.sourcedir.path,
        "sourcedir_slug": sourcedir_slug,
        "sourcefile": sourcefile_entry.filename,
        "sourcefile_slug": sourcefile_slug,
        "sourcefile_type": sourcefile_entry.sourcefile_type,
        "sourcefile_entry": sourcefile_entry,
        "metadata": metadata,
        "nav_info": nav_info,
        "already_processed": already_processed,
        "available_sourcedirs": available_sourcedirs,
    }


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/text"
)
def inspect_sourcefile_text(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the text content of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # Get existing linked wordforms from database
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # Get phrases from database
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create enhanced text with interactive word links
        enhanced_original_txt, found_wordforms = create_interactive_word_links(
            text=str(sourcefile_entry.text_target or ""),
            wordforms=wordforms_d,
            target_language_code=target_language_code,
        )

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(wordforms_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "enhanced_original_txt": enhanced_original_txt,
                "translated_txt": sourcefile_entry.text_english,
                "active_tab": "text",
                "wordforms_d": wordforms_d,
                "phrases_d": phrases_d,
            }
        )

        return render_template("sourcefile_text.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/words"
)
def inspect_sourcefile_words(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the words and phrases of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # Get existing linked wordforms from database with optimized query
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # For the words view, we only need phrases count for the tab, not full data
        phrases_count = _get_phrases_count(sourcefile_entry)
        # But for backward compatibility, we'll still get the full phrases data
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(wordforms_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "active_tab": "words",
                "wordforms_d": wordforms_d,
                "phrases_d": phrases_d,
            }
        )

        return render_template("sourcefile_words.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/phrases"
)
def inspect_sourcefile_phrases(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the phrases of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # For the phrases view, we only need wordforms count for the tab, not full data
        wordforms_count = _get_wordforms_count(sourcefile_entry)
        # But for backward compatibility, we'll still get the full wordforms data
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # Get phrases data with optimized query
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(phrases_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "active_tab": "phrases",
                "phrases_d": phrases_d,
                "wordforms_d": wordforms_d,
            }
        )

        return render_template("sourcefile_phrases.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


def access_sourcefile(
    target_language_code: str,
    sourcedir_slug: str,
    sourcefile_slug: str,
    *,
    as_attachment: bool = False,
):
    """Helper function to access source files."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(str(sourcefile_entry.filename)).suffix
        ) as temp_file:
            # Write the content to the temporary file based on type
            if sourcefile_entry.sourcefile_type in ["audio", "youtube_audio"]:
                if sourcefile_entry.audio_data is None:
                    abort(404, description="Audio content not found")
                temp_file.write(bytes(sourcefile_entry.audio_data))
            else:  # image type
                if sourcefile_entry.image_data is None:
                    abort(404, description="Image content not found")
                temp_file.write(bytes(sourcefile_entry.image_data))
            temp_file.flush()

            # Map common file extensions to MIME types
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".pdf": "application/pdf",
                ".txt": "text/plain",
                ".mp3": "audio/mpeg",
            }
            suffix = Path(str(sourcefile_entry.filename)).suffix.lower()
            mimetype = mime_types.get(suffix, "application/octet-stream")

            response = send_file(
                temp_file.name,
                mimetype=mimetype,
                as_attachment=as_attachment,
            )
            if as_attachment:
                # Sanitize filename for Content-Disposition header
                safe_filename = (
                    str(sourcefile_entry.filename).encode("ascii", "ignore").decode()
                )
                if not safe_filename:  # If filename becomes empty after sanitization
                    safe_filename = sourcefile_slug + suffix
                response.headers["Content-Disposition"] = (
                    f'attachment; filename="{safe_filename}"'
                )
            return response
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/view"
)
def view_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """View the source file."""
    return access_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, as_attachment=False
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/download"
)
def download_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Download the source file."""
    return access_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, as_attachment=True
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process"
)
def process_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process a source file to extract wordforms and phrases."""
    try:
        # Get the sourcedir entry using helper
        sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

        # Get the sourcefile entry by slug
        sourcefile_entry = Sourcefile.get(
            Sourcefile.sourcedir == sourcedir_entry,
            Sourcefile.slug == sourcefile_slug,
        )

        target_language_name = get_language_name(target_language_code)

        try:
            # Process the sourcefile content
            source, tricky_words_d, extra_metadata = process_sourcefile_content(
                sourcefile_entry,
                target_language_name,
            )

            # Update sourcefile with processed data
            sourcefile_entry.text_target = source["txt_tgt"]
            sourcefile_entry.text_english = source["txt_en"]
            # Make sure metadata is JSON-serializable
            # Use gjdutils jsonify to handle any potential non-serializable objects
            safe_metadata = json.loads(
                jsonify(
                    {
                        **extra_metadata,  # Include duration, language, etc.
                        "words": tricky_words_d,  # Keep word data for debugging
                    }
                )
            )

            # Store the safe serializable metadata
            sourcefile_entry.metadata = safe_metadata
            sourcefile_entry.save()

            # Create database entries for words
            for word_counter, word_d in enumerate(tricky_words_d):
                # Try to get existing lemma or create new one
                lemma, lemma_created = Lemma.update_or_create(
                    lookup={
                        "lemma": word_d["lemma"],
                        "language_code": target_language_code,
                    },
                    updates={
                        "part_of_speech": word_d["part_of_speech"],
                        "translations": word_d["translations"],
                        "is_complete": False,  # Mark as incomplete until full metadata is added
                    },
                )

                # Try to get existing wordform or create new one
                wordform, wordform_created = Wordform.update_or_create(
                    lookup={
                        "wordform": word_d["wordform"],
                        "language_code": target_language_code,
                    },
                    updates={
                        "lemma_entry": lemma,
                        "part_of_speech": word_d["part_of_speech"],
                        "translations": word_d["translations"],
                        "inflection_type": word_d["inflection_type"],
                        "is_lemma": word_d["wordform"] == word_d["lemma"],
                    },
                )

                # Create SourcefileWordform entry
                SourcefileWordform.update_or_create(
                    lookup={
                        "sourcefile": sourcefile_entry,
                        "wordform": wordform,
                    },
                    updates={
                        "centrality": word_d["centrality"],
                        "ordering": word_counter + 1,
                    },
                )

            flash("File processed successfully")
        except Exception as e:
            # If processing fails, mark it as failed
            sourcefile_entry.metadata = {"processing_failed": True, "error": str(e)}
            sourcefile_entry.save()
            flash("Processing failed: " + str(e))

        return redirect(
            url_for(
                "sourcefile_views.inspect_sourcefile",
                target_language_code=target_language_code,
                sourcedir_slug=sourcedir_slug,
                sourcefile_slug=sourcefile_slug,
            )
        )

    except DoesNotExist:
        return "Source file not found", 404
    except Exception as e:
        flash(f"Processing failed: {str(e)}")
        return redirect(request.referrer)


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/audio"
)
def play_sourcefile_audio(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Play the audio file associated with the source file."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Create a temporary file to store the content
        audio_filename = Path(str(sourcefile_entry.filename)).with_suffix(".mp3").name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            # Write the audio content to the temporary file
            if sourcefile_entry.audio_data is None:
                abort(404, description="Audio content not found")
            temp_file.write(bytes(sourcefile_entry.audio_data))
            temp_file.flush()

            return send_file(
                temp_file.name, mimetype="audio/mpeg", download_name=audio_filename
            )
    except DoesNotExist:
        abort(404, description="Audio file not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/update"
)
def update_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Get more tricky words from an already processed source file."""
    # Get the sourcedir entry
    sourcedir_entry = _get_sourcedir_entry(target_language_code, sourcedir_slug)

    # Get the sourcefile entry
    sourcefile_entry = Sourcefile.get(
        Sourcefile.sourcedir == sourcedir_entry,
        Sourcefile.slug == sourcefile_slug,
    )

    # Get existing wordforms to ignore
    existing_wordforms = [
        wf.wordform.wordform  # Access through the junction table
        for wf in sourcefile_entry.wordform_entries.select()
    ]

    # Get original text
    txt_tgt = sourcefile_entry.text_target
    if not txt_tgt:
        abort(400, description="No target language text found in source file")

    # Get more tricky words, ignoring existing ones
    target_language_name = get_language_name(target_language_code)
    tricky_d, extra = extract_tricky_words_or_phrases(
        txt_tgt,
        target_language_name=target_language_name,
        language_level=LANGUAGE_LEVEL,
        ignore_words=existing_wordforms,
        verbose=1,
    )

    # Process new words and create database entries
    if isinstance(tricky_d, dict) and "wordforms" in tricky_d:
        for word_d in tricky_d["wordforms"]:
            # Try to get existing lemma or create new one
            lemma, lemma_created = Lemma.get_or_create(
                lemma=word_d["lemma"],
                language_code=target_language_code,
                defaults={
                    "part_of_speech": word_d["part_of_speech"],
                    "translations": word_d["translations"],
                    "is_complete": False,  # Mark as incomplete until full metadata is added
                },
            )

            # Try to get existing wordform or create new one
            wordform, wordform_created = Wordform.get_or_create(
                wordform=word_d["wordform"],
                language_code=target_language_code,
                defaults={
                    "lemma_entry": lemma,
                    "part_of_speech": word_d["part_of_speech"],
                    "translations": word_d["translations"],
                    "inflection_type": word_d["inflection_type"],
                    "is_lemma": word_d["wordform"] == word_d["lemma"],
                },
            )

            # Create SourcefileWordform entry
            SourcefileWordform.get_or_create(
                sourcefile=sourcefile_entry,
                wordform=wordform,
                defaults={
                    "centrality": word_d["centrality"],
                    "ordering": len(existing_wordforms) + 1,
                },
            )

        # Update metadata for debugging/comparison
        if sourcefile_entry.metadata is None:
            sourcefile_entry.metadata = {}
        if "words" not in sourcefile_entry.metadata:
            sourcefile_entry.metadata["words"] = []
        sourcefile_entry.metadata["words"].extend(tricky_d["wordforms"])
        sourcefile_entry.save()

    return redirect(
        url_for(
            "sourcefile_views.inspect_sourcefile",
            target_language_code=target_language_code,
            sourcedir_slug=sourcedir_slug,
            sourcefile_slug=sourcefile_slug,
        )
    )


def _process_individual_lemma(lemma: str, target_language_code: str):
    """Process a single lemma, generating metadata and audio for its sentences.

    Includes random jitter to avoid overwhelming external APIs."""
    # Add jitter delay between 0 and 2 seconds
    time.sleep(random.uniform(0, 2))

    try:
        metadata = load_or_generate_lemma_metadata(
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


@sourcefile_views_bp.route(
    "/api/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_individual",
    methods=["POST"],
)
def process_individual_words(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process individual words in a sourcefile, generating full metadata and audio."""
    # Get the sourcefile entry
    sourcefile_entry = _get_sourcefile_entry(
        target_language_code, sourcedir_slug, sourcefile_slug
    )

    # Get all wordforms for this sourcefile
    wordforms = [sw.wordform for sw in sourcefile_entry.wordform_entries]  # type: ignore

    # Get unique lemmas through the lemma_entry relationship
    unique_lemmas = {wf.lemma_entry.lemma for wf in wordforms}

    # Process lemmas in parallel with a thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all tasks
        futures = [
            executor.submit(_process_individual_lemma, lemma, target_language_code)
            for lemma in unique_lemmas
        ]

        # Wait for all tasks to complete
        for future in futures:
            try:
                future.result()  # This will raise any exceptions from the thread
            except Exception as e:
                print(f"Thread failed: {str(e)}")
                # Continue processing other lemmas even if one fails

    print(f"Done processing sourcefile {sourcefile_slug}")
    return "", 204


@sourcefile_views_bp.route(
    "/api/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/update_description",
    methods=["PUT"],
)
def update_sourcefile_description(
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


@sourcefile_views_bp.route(
    "/api/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/move",
    methods=["PUT"],
)
def move_sourcefile(
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
                Sourcedir.language_code == target_language_code,
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


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/sentences"
)
def sourcefile_sentences(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Show sentences for a sourcefile."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get sourcedir and sourcefile
        sourcedir = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.language_code == target_language_code,
        )
        sourcefile = Sourcefile.get(
            Sourcefile.slug == sourcefile_slug,
            Sourcefile.sourcedir == sourcedir,
        )

        # Get lemmas from sourcefile's wordforms
        lemmas = get_sourcefile_lemmas(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get sentences containing any of these lemmas
        matching_sentences = [
            s
            for s in get_all_sentences(target_language_code)
            if s.get("lemma_words")
            and any(lemma in s["lemma_words"] for lemma in lemmas)
        ]

        # Get the first matching sentence for initial display
        sentence = matching_sentences[0] if matching_sentences else None

        return render_template(
            "sentence_flashcards.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sourcedir=sourcedir,
            sourcefile=sourcefile,
            lemmas=lemmas,
            sentence=sentence,
        )
    except DoesNotExist:
        abort(404, description="Source file not found")


@sourcefile_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>",
    methods=["DELETE"],
)
def delete_sourcefile(
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


@sourcefile_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/rename",
    methods=["PUT"],
)
def rename_sourcefile(
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


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/next"
)
def next_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Navigate to the next sourcefile alphabetically."""
    return _navigate_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, increment=1
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/prev"
)
def prev_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Navigate to the previous sourcefile alphabetically."""
    return _navigate_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, increment=-1
    )


@sourcefile_views_bp.route(
    "/api/sourcedir/<target_language_code>/<sourcedir_slug>/create_from_text",
    methods=["POST"],
)
def create_sourcefile_from_text(target_language_code: str, sourcedir_slug: str):
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

        if not title:
            return jsonify({"error": "Title is required"}), 400
        if not text_target:
            return jsonify({"error": "Text content is required"}), 400

        # Use the original title as filename (with .txt extension)
        filename = f"{title}.txt"

        # Check if file already exists
        if (
            Sourcefile.select()
            .where(
                (Sourcefile.sourcedir == sourcedir_entry)
                & (Sourcefile.filename == filename)
            )
            .exists()
        ):
            return jsonify({"error": f"File {filename} already exists"}), 409

        # Create sourcefile entry
        sourcefile = Sourcefile.create(
            sourcedir=sourcedir_entry,
            filename=filename,
            text_target=text_target,
            text_english="",  # Will be populated during processing
            metadata={},
            sourcefile_type="text",
        )

        return (
            jsonify(
                {
                    "message": "Successfully created file",
                    "filename": filename,
                    "slug": sourcefile.slug,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in create_sourcefile_from_text: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sourcefile_views_bp.route(
    "/<language_code>/<sourcedir_slug>/add_from_youtube", methods=["POST"]
)
def add_sourcefile_from_youtube(language_code, sourcedir_slug):
    """Add a new sourcefile from a YouTube video's audio."""
    sourcedir = get_sourcedir_or_404(language_code, sourcedir_slug)

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


@sourcefile_views_bp.route(
    "/api/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate_audio",
    methods=["POST"],
)
def generate_sourcefile_audio(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Generate audio for a sourcefile using ElevenLabs."""
    temp_file = None
    try:
        sourcefile_entry = (
            Sourcefile.select()
            .join(Sourcedir)
            .where(
                (Sourcedir.language_code == target_language_code)
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
                api_key=ELEVENLABS_API_KEY.get_secret_value(),
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
