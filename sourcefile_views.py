import os
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
from env_config import ELEVENLABS_API_KEY
from audio_utils import add_delays, ensure_model_audio_data
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
from gdutils.outloud_text_to_speech import outloud_elevenlabs
from lang_utils import get_language_name
from sentence_utils import generate_practice_sentences, get_all_sentences
from sourcedir_utils import (
    _get_navigation_info,
    _get_sourcedir_entry,
    _get_sourcefile_entry,
    _navigate_sourcefile,
    get_sourcedir_or_404,
)
from sourcefile_processing import process_sourcefile_content
from store_utils import load_or_generate_lemma_metadata
from vocab_llm_utils import (
    create_interactive_word_links,
    extract_tricky_words_or_phrases,
    normalize_text,
)
from youtube_utils import YouTubeDownloadError, download_audio
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import time
from word_utils import get_sourcefile_lemmas

sourcefile_views_bp = Blueprint("sourcefile_views", __name__)


@sourcefile_views_bp.route("/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>")
def inspect_sourcefile(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the contents and metadata of a source file."""
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
        existing_wordforms_d = {}  # Dict for quick lookup by wordform string
        existing_wordform_ids = set()  # Track existing wordform IDs
        for sourcefile_wordform in sourcefile_entry.wordform_entries:  # type: ignore
            wordform = sourcefile_wordform.wordform
            wordform_d = wordform.to_dict()
            # Add centrality and ordering from junction table
            wordform_d["centrality"] = sourcefile_wordform.centrality
            wordform_d["ordering"] = sourcefile_wordform.ordering
            existing_wordforms_d[wordform.wordform.lower()] = wordform_d
            existing_wordform_ids.add(wordform.id)

        # Extract tokens from the text
        from vocab_llm_utils import extract_tokens

        tokens_in_text = extract_tokens(str(sourcefile_entry.text_target or ""))

        # Query database for matching wordforms
        wordforms = list(
            Wordform.select().where((Wordform.language_code == target_language_code))
        )

        # Filter wordforms in Python using normalize_text
        normalized_tokens = {normalize_text(t) for t in tokens_in_text}
        wordforms = [
            wf for wf in wordforms if normalize_text(wf.wordform) in normalized_tokens
        ]

        # Convert to dictionary structure and merge with existing
        for wordform in wordforms:
            wordform_str = wordform.wordform.lower()
            if wordform_str not in existing_wordforms_d:
                # Create new SourcefileWordform entry
                SourcefileWordform.create(
                    sourcefile=sourcefile_entry,
                    wordform=wordform,
                    centrality=0.3,  # Default centrality for auto-discovered words
                    ordering=len(existing_wordforms_d) + 1,
                )
                # Add to our dictionaries
                wordform_d = wordform.to_dict()
                wordform_d["centrality"] = 0.3
                wordform_d["ordering"] = len(existing_wordforms_d) + 1
                existing_wordforms_d[wordform_str] = wordform_d
                existing_wordform_ids.add(wordform.id)

        # Create enhanced text with interactive word links
        enhanced_original_txt, found_wordforms = create_interactive_word_links(
            text=str(sourcefile_entry.text_target or ""),
            wordforms=list(existing_wordforms_d.values()),
            target_language_code=target_language_code,
        )

        # Get unique lemmas from wordforms
        unique_lemmas = {
            wordform_d["lemma"]
            for wordform_d in list(existing_wordforms_d.values())
            if "lemma" in wordform_d
        }

        # Load metadata for each lemma
        lemma_metadata = {}
        for lemma in unique_lemmas:
            try:
                metadata = load_or_generate_lemma_metadata(lemma, target_language_code)
                lemma_metadata[lemma] = metadata
            except FileNotFoundError:
                lemma_metadata[lemma] = {
                    "translations": [],
                    "etymology": "",
                    "commonality": 0.5,
                }

        # Get phrases from database
        phrases_d = []
        for sourcefile_phrase in (
            sourcefile_entry.phrase_entries.select()  # type: ignore
            .join(Phrase)
            .order_by(SourcefilePhrase.ordering)
        ):
            phrase = sourcefile_phrase.phrase
            phrase_d = {
                "canonical_form": phrase.canonical_form,
                "raw_forms": phrase.raw_forms,
                "translations": phrase.translations,
                "part_of_speech": phrase.part_of_speech,
                "register": phrase.register,
                "commonality": phrase.commonality,
                "guessability": phrase.guessability,
                "etymology": phrase.etymology,
                "cultural_context": phrase.cultural_context,
                "mnemonics": phrase.mnemonics,
                "component_words": phrase.component_words,
                "usage_notes": phrase.usage_notes,
                "difficulty_level": phrase.difficulty_level,
                "centrality": sourcefile_phrase.centrality,
                "ordering": sourcefile_phrase.ordering,
            }
            phrases_d.append(phrase_d)

        # Prepare metadata for template
        metadata = {
            "created_at": sourcefile_entry.created_at,
            "updated_at": sourcefile_entry.updated_at,
        }
        if (
            sourcefile_entry.metadata
            and "image_processing" in sourcefile_entry.metadata
        ):
            metadata["image_processing"] = sourcefile_entry.metadata["image_processing"]

        # Check if file has been processed before
        already_processed = bool(list(existing_wordforms_d.values()))

        return render_template(
            "sourcefile.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sourcedir=sourcefile_entry.sourcedir.path,  # Use path for display
            sourcedir_slug=sourcedir_slug,  # Use slug for URLs
            sourcefile=sourcefile_entry.filename,  # Use filename for display
            sourcefile_slug=sourcefile_slug,  # Use slug for URLs
            sourcefile_type=sourcefile_entry.sourcefile_type,  # Add sourcefile type for icon
            sourcefile_entry=sourcefile_entry,  # Pass the full sourcefile entry
            enhanced_original_txt=enhanced_original_txt,
            translated_txt=sourcefile_entry.text_english,
            wordforms_d=list(existing_wordforms_d.values()),
            lemma_metadata=lemma_metadata,
            phrases_d=phrases_d,
            metadata=metadata,
            already_processed=already_processed,
            nav_info=nav_info,
        )
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
            # Merge extra metadata with words data
            sourcefile_entry.metadata = {
                **extra_metadata,  # Include duration, language, etc.
                "words": tricky_words_d,  # Keep word data for debugging
            }
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
        lemmas = get_sourcefile_lemmas(target_language_code, sourcefile_slug)

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

        # Generate filename with .txt extension
        filename = f"{slugify(title)}.txt"

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
                api_key=ELEVENLABS_API_KEY,
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
    with ThreadPoolExecutor(max_workers=5) as executor:
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
