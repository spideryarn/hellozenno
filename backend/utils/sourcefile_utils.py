# External imports
import os
import tempfile
import json
from typing import Optional, cast, Dict, Any
from pathlib import Path
import random
from bs4 import BeautifulSoup

# Internal imports
from config import (
    DEFAULT_MAX_NEW_WORDS_PER_PROCESSING,
    DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING,
    MAX_IMAGE_SIZE_FOR_STORAGE,
    MAX_AUDIO_SIZE_FOR_STORAGE,
    SOURCE_IMAGE_EXTENSIONS,
    TEXT_SOURCE_EXTENSIONS,
)
from db_models import (
    Lemma,
    Sourcefile,
    Wordform,
    SourcefileWordform,
    SourcefilePhrase,
    Sourcedir,
)
from utils.audio_utils import transcribe_audio
from gjdutils.dt import dt_str
from gjdutils.jsons import jsonify
from utils.image_utils import resize_image_to_target_size
from utils.misc_utils import pop_multi

# Removed - no longer using asynchronous processing
# from utils.parallelisation_utils import run_async
from utils.sourcedir_utils import _get_sourcedir_entry, _get_navigation_info
from utils.lang_utils import get_language_name
from utils.store_utils import load_or_generate_lemma_metadata
from utils.types import LanguageLevel
from utils.vocab_llm_utils import (
    extract_text_from_image,
    translate_to_english,
    extract_tricky_words,
    process_phrases_from_text,
    create_interactive_word_links,
    metadata_for_lemma_full,
)

"""
This module handles processing of sourcefiles in different formats.

Supported sourcefile types:
- text: Direct text input, stored in text_target field
- image: Image files that contain text, stored in image_data field
       Text is extracted using OCR during processing
- audio: Audio files (MP3), stored in audio_data field
       Text is extracted using Whisper API during processing

The processing pipeline is the same for all types:
1. Extract text (from direct input, OCR, or speech-to-text)
2. Translate to English
3. Extract vocabulary
4. Create database entries
"""


def get_text_from_sourcefile(
    sourcefile_entry, target_language_name: str
) -> tuple[str, dict]:
    """Extract text from sourcefile based on its type, e.g. transcribe image/audio."""
    if sourcefile_entry.sourcefile_type == "text":
        if not sourcefile_entry.text_target:
            raise ValueError("No text content found")
        return sourcefile_entry.text_target, {}

    elif sourcefile_entry.sourcefile_type == "image":
        if sourcefile_entry.image_data is None:
            raise ValueError("No image data found")

        # Get original file extension
        ext = Path(sourcefile_entry.filename).suffix.lower()
        assert (
            ext in SOURCE_IMAGE_EXTENSIONS
        ), f"No appropriate extension found for {sourcefile_entry.filename}"

        # Create temp file for image processing with original extension
        with tempfile.NamedTemporaryFile(suffix=ext) as temp_file:
            temp_file.write(sourcefile_entry.image_data)
            temp_file.flush()
            txt_tgt, extra = extract_text_from_image(
                temp_file.name, target_language_name, verbose=1
            )
            if "llm_extra" in extra:
                pop_multi(
                    extra["llm_extra"],
                    ["extra", "client", "contents", "extract_json_from_markdown"],
                )
            return txt_tgt, extra

    elif sourcefile_entry.sourcefile_type in ["audio", "youtube_audio"]:
        if sourcefile_entry.audio_data is None:
            raise ValueError("No audio data found")

        # For YouTube audio, first check if we have subtitles in metadata
        if (
            sourcefile_entry.sourcefile_type == "youtube_audio"
            and sourcefile_entry.metadata
        ):
            subtitle_content = sourcefile_entry.metadata.get("subtitle_content")
            if subtitle_content:
                # Clean up VTT format to get just the text
                cleaned_text = []
                for line in subtitle_content.splitlines():
                    # Skip WebVTT headers and timing lines
                    if (
                        not line.strip()
                        or line.startswith("WEBVTT")
                        or "-->" in line
                        or line[0].isdigit()
                    ):
                        continue
                    cleaned_text.append(line.strip())

                txt_tgt = "\n".join(cleaned_text)

                # Return the subtitle content and add metadata about its source
                return txt_tgt, {
                    "text_source": "youtube_subtitles",
                    "subtitle_source": sourcefile_entry.metadata.get(
                        "subtitle_source", "unknown"
                    ),
                    "is_likely_music": sourcefile_entry.metadata.get(
                        "is_likely_music", False
                    ),
                }

        # If no subtitles or not YouTube, fall back to Whisper transcription
        # Create a temporary file with the correct extension
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(sourcefile_entry.audio_data)
            temp_file.flush()

            # Convert language name to code for Whisper API
            target_language_code = sourcefile_entry.sourcedir.target_language_code
            txt_tgt, extra = transcribe_audio(
                Path(temp_file.name), target_language_code
            )

            try:
                os.unlink(temp_file.name)  # Clean up temp file
            except OSError:
                # Ignore file cleanup errors - temp file will be cleaned up by OS eventually
                pass

            # Add text source to metadata
            extra["text_source"] = "whisper_transcription"

            # Make extra metadata JSON-serializable
            if extra:
                extra = json.loads(jsonify(extra))

            return txt_tgt, extra

    else:
        raise ValueError(
            f"Unsupported sourcefile type: {sourcefile_entry.sourcefile_type}"
        )


def process_uploaded_file(
    file_content: bytes,
    original_filename: str,
    sourcedir_path: str,
    target_language_code: str,
) -> tuple[bytes, str, dict]:
    """Process an uploaded file, handling resizing and filename generation.

    Args:
        file_content: The raw file content
        original_filename: The original filename
        sourcedir_path: The path of the source directory
        target_language_code: The language code

    Returns:
        tuple of (processed_content, final_filename, metadata)
    """
    # Get original filename and extension
    # original_filename = secure_filename(original_filename)
    ext = Path(original_filename).suffix.lower()

    # If it's a generic image/audio name, rename it with timestamp
    generic_names = {
        "image.jpg",
        "image.jpeg",
        "image.png",
        "photo.jpg",
        "photo.jpeg",
        "photo.png",
        "audio.mp3",
        "recording.mp3",
        "voice.mp3",
    }
    if original_filename.lower() in generic_names:
        filename = f"{dt_str()}_{sourcedir_path}_{target_language_code}{ext}"
    else:
        filename = original_filename

    metadata = {}

    # Process based on file type
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
        # Resize image if needed
        try:
            file_content, resize_metadata = resize_image_to_target_size(
                file_content, MAX_IMAGE_SIZE_FOR_STORAGE
            )
            if resize_metadata.get("was_resized"):
                metadata["image_processing"] = resize_metadata
        except (ValueError, IOError) as e:
            raise ValueError(f"Error processing {filename}: {str(e)}")

    elif ext in TEXT_SOURCE_EXTENSIONS:
        # Process text file according to format
        try:
            # Decode the content as text
            text_content = file_content.decode("utf-8")

            # Check if there's a separator for description
            separator = "----"
            if separator in text_content:
                # Split at the first occurrence of the separator
                parts = text_content.split(separator, 1)
                description = parts[0].strip()
                text = parts[1].strip()
                metadata["description"] = description
                # Return only the text part as file content (description stored in metadata)
                file_content = text.encode("utf-8")
            else:
                # No separator, treat the entire content as text
                metadata["description"] = None

            # Add file format info to metadata
            metadata["text_format"] = "markdown" if ext == ".md" else "plain"

        except UnicodeDecodeError:
            raise ValueError(f"The file {filename} is not a valid text file")

    elif ext == ".mp3":
        # For audio, just verify it's a valid MP3 file
        # We could add audio validation here if needed
        if len(file_content) > MAX_AUDIO_SIZE_FOR_STORAGE:
            raise ValueError(
                f"Audio file too large (max {MAX_AUDIO_SIZE_FOR_STORAGE // (1024*1024)}MB)"
            )

    return file_content, filename, metadata


def _get_sourcefile_entry(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
) -> Sourcefile:
    """Helper function to get sourcefile entry by slug with language code."""
    sourcedir = _get_sourcedir_entry(target_language_code, sourcedir_slug)
    return Sourcefile.get(
        Sourcefile.sourcedir == sourcedir,
        Sourcefile.slug == sourcefile_slug,
    )


def ensure_text_extracted(sourcefile_entry):
    """Extract text if not already present based on sourcefile type."""
    if sourcefile_entry.text_target:
        return sourcefile_entry
    target_language_name = get_language_name(
        sourcefile_entry.sourcedir.target_language_code
    )
    extracted_text, extra_metadata = get_text_from_sourcefile(
        sourcefile_entry, target_language_name
    )
    pop_multi(extra_metadata, ["extract_json_from_markdown"])
    if sourcefile_entry.metadata is None:
        sourcefile_entry.metadata = {}
    sourcefile_entry.metadata.update(extra_metadata)
    sourcefile_entry.text_target = extracted_text
    sourcefile_entry.save()
    return sourcefile_entry


def ensure_translation(sourcefile_entry):
    """Translate text if not already present"""
    if sourcefile_entry.text_english:
        return sourcefile_entry
    if not sourcefile_entry.text_target:
        sourcefile_entry = ensure_text_extracted(sourcefile_entry)
    target_language_name = get_language_name(
        sourcefile_entry.sourcedir.target_language_code
    )
    translated_text, translation_metadata = translate_to_english(
        sourcefile_entry.text_target, target_language_name, verbose=1
    )
    pop_multi(
        translation_metadata,
        ["response", "extract_json_from_markdown", "client", "extra"],
    )
    sourcefile_entry.text_english = translated_text
    if sourcefile_entry.metadata is None:
        sourcefile_entry.metadata = {}
    sourcefile_entry.metadata["translation"] = translation_metadata
    sourcefile_entry.save()
    return sourcefile_entry


def _store_word_in_database(
    sourcefile_entry: Sourcefile,
    word_d: dict,
    ordering: int,
    target_language_code: str,
):
    """Store a single wordform and its lemma in the database."""
    lemma, _ = Lemma.update_or_create(
        lookup={
            "lemma": word_d["lemma"],
            "target_language_code": target_language_code,
        },
        updates={
            "part_of_speech": word_d["part_of_speech"],
            "translations": word_d["translations"],
            "is_complete": False,
        },
    )
    wordform, _ = Wordform.update_or_create(
        lookup={
            "wordform": word_d["wordform"],
            "target_language_code": target_language_code,
        },
        updates={
            "lemma_entry": lemma,
            "part_of_speech": word_d["part_of_speech"],
            "translations": word_d["translations"],
            "inflection_type": word_d["inflection_type"],
            "is_lemma": word_d["wordform"] == word_d["lemma"],
        },
    )
    sourcefilewordform, _ = SourcefileWordform.update_or_create(
        lookup={
            "sourcefile": sourcefile_entry,
            "wordform": wordform,
        },
        updates={
            "centrality": word_d["centrality"],
            "ordering": ordering,
        },
    )
    return wordform, lemma, sourcefilewordform


def ensure_tricky_wordforms(
    sourcefile_entry: Sourcefile,
    language_level: LanguageLevel,
    max_new_words: Optional[int],
):
    """Extract vocabulary to reach specified count.

    Args:
        max_new_words: Maximum number of words to extract (0 to skip, None for no limit)
    """
    extra = locals()
    extra.pop("sourcefile_entry")
    if max_new_words == 0:
        return sourcefile_entry, {}
    assert sourcefile_entry.text_target, "Text must have been extracted first"
    # Get existing wordforms - Note: wordform_entries is a backref from SourcefileWordform
    existing_wordforms = []
    for wf_entry in SourcefileWordform.select().where(
        SourcefileWordform.sourcefile == sourcefile_entry
    ):
        if wf_entry.wordform and wf_entry.wordform.wordform:
            existing_wordforms.append(wf_entry.wordform.wordform)
    target_language_code = sourcefile_entry.sourcedir.target_language_code
    target_language_name = get_language_name(target_language_code)
    # Extract more vocabulary - ensure text_target is a string
    tricky_d, tricky_extra = extract_tricky_words(
        str(sourcefile_entry.text_target),
        target_language_name=target_language_name,
        language_level=language_level,
        max_new_words=max_new_words,
        ignore_words=existing_wordforms,
    )
    # Process new words and update database
    new_wordforms = tricky_d["wordforms"][:max_new_words]
    lemmas = []
    for word_counter, word_d in enumerate(new_wordforms):
        wordform, lemma, sourcefilewordform = _store_word_in_database(
            sourcefile_entry,
            word_d,
            len(existing_wordforms) + word_counter + 1,
            target_language_code,
        )
        lemmas.append(lemma)
    # for counter, lemma in enumerate(lemmas):
    #     delay = counter * 10
    #     run_async(
    #         load_or_generate_lemma_metadata,
    #         lemma.lemma,
    #         target_language_code,
    #         generate_if_incomplete=True,
    #         delay=delay,
    #     )
    extra.update({"tricky_d": tricky_d, "tricky_extra": tricky_extra})
    return sourcefile_entry, extra


def ensure_tricky_phrases(
    sourcefile_entry: Sourcefile,
    language_level: LanguageLevel,
    max_new_phrases: Optional[int],
    verbose: int = 0,
):
    """Extract tricky phrases from text."""
    extra = locals()
    extra.pop("sourcefile_entry")
    if max_new_phrases is None or max_new_phrases == 0:
        return sourcefile_entry, {}
    assert sourcefile_entry.text_target, "Text must have been extracted first"
    target_language_code = sourcefile_entry.sourcedir.target_language_code
    target_language_name = get_language_name(target_language_code)
    phrases_extra = process_phrases_from_text(
        str(sourcefile_entry.text_target),
        target_language_name,
        target_language_code,
        language_level=language_level,
        max_new_phrases=max_new_phrases,
        sourcefile_entry=sourcefile_entry,
        verbose=verbose,
    )
    extra.update({"phrases_extra": phrases_extra})
    return sourcefile_entry, extra


def get_sourcefile_details(
    sourcefile_entry: Sourcefile,
    target_language_code: str,
    purpose="basic",  # "basic", "text", "words", "phrases", "translation", "image", or "audio"
):
    """Get details for a sourcefile based on the specific purpose needed.

    Args:
        sourcefile_entry: The Sourcefile object
        target_language_code: The language code
        purpose: What the data will be used for ("basic", "text", "words", "phrases", "translation", "image", or "audio")

    Returns:
        A dictionary with the data needed for the specified purpose
    """
    from utils.sourcedir_utils import _get_navigation_info
    from db_models import SourcefileWordform, SourcefilePhrase, Sourcedir

    # Get navigation info (needed by all views)
    # First, ensure we're directly accessing the Sourcedir object, not the ForeignKeyField
    # In practice, we can directly access the related model with sourcefile_entry.sourcedir
    # Type annotations are added to satisfy the linter
    sourcedir = cast(Sourcedir, sourcefile_entry.sourcedir)

    nav_info = _get_navigation_info(
        sourcedir=sourcedir, sourcefile_slug=str(sourcefile_entry.slug)
    )

    # Always get counts efficiently (these are small and needed for all tab navigation)
    wordforms_count = (
        SourcefileWordform.select()
        .where(SourcefileWordform.sourcefile == sourcefile_entry)
        .count()
    )

    phrases_count = (
        SourcefilePhrase.select()
        .where(SourcefilePhrase.sourcefile == sourcefile_entry)
        .count()
    )

    # Create basic result structure (common to all endpoints)
    # Note: We're directly accessing the id field which is available at runtime
    # even though it's not explicitly declared in the model class
    result = {
        "sourcefile": {
            # Type ignored because Peewee models have this field at runtime
            "id": sourcefile_entry.id,  # type: ignore
            "filename": sourcefile_entry.filename,
            "slug": sourcefile_entry.slug,
            "description": sourcefile_entry.description,
            "sourcefile_type": sourcefile_entry.sourcefile_type,
            "has_audio": bool(sourcefile_entry.audio_data),
            "has_image": bool(sourcefile_entry.image_data),
        },
        "sourcedir": {
            # Type ignored because Peewee models have this field at runtime
            "id": sourcedir.id,  # type: ignore
            "path": sourcedir.path,
            "slug": sourcedir.slug,
            "target_language_code": sourcedir.target_language_code,
        },
        "metadata": {
            "created_at": sourcefile_entry.created_at,
            "updated_at": sourcefile_entry.updated_at,
        },
        "navigation": nav_info,
        "stats": {
            "wordforms_count": wordforms_count,
            "phrases_count": phrases_count,
            "already_processed": bool(sourcefile_entry.text_target),
        },
    }

    # Add metadata from sourcefile if it exists
    if sourcefile_entry.metadata and "image_processing" in sourcefile_entry.metadata:
        result["metadata"]["image_processing"] = sourcefile_entry.metadata[
            "image_processing"
        ]

    # Add purpose-specific data
    if purpose in ["text", "translation"]:
        # Add text content for both text and translation tabs
        result["sourcefile"]["text_target"] = sourcefile_entry.text_target
        result["sourcefile"]["text_english"] = sourcefile_entry.text_english

    # Generate enhanced text only for text tab (requires wordforms)
    if purpose == "text" and sourcefile_entry.text_target:
        from utils.vocab_llm_utils import (
            create_interactive_word_links,
            create_interactive_word_data,
        )
        from db_models import Wordform

        # Get minimal wordform data needed for links
        wordforms_for_links = Wordform.get_all_wordforms_for(
            target_language_code=target_language_code,
            sourcefile=sourcefile_entry,
            include_junction_data=True,
        )

        # DEPRECATED: Generate backward-compatible HTML for old components
        # This approach mixes content with presentation and should be removed once
        # all frontend components have been updated to use the structured data approach
        enhanced_text, found_wordforms_html = create_interactive_word_links(
            text=str(sourcefile_entry.text_target),
            wordforms=wordforms_for_links,
            target_language_code=target_language_code,
        )

        # Generate new structured data format for the updated component
        recognized_words, found_wordforms_data = create_interactive_word_data(
            text=str(sourcefile_entry.text_target),
            wordforms=wordforms_for_links,
            target_language_code=target_language_code,
        )

        # Include both formats in the response
        result["enhanced_text"] = enhanced_text  # Legacy format (HTML)
        result["recognized_words"] = recognized_words  # New format (structured data)
        result["text_data"] = {
            "text": str(sourcefile_entry.text_target),  # Original plain text
            "recognized_words": recognized_words,  # Words with positions and metadata
        }

        # Include wordforms in the result so the frontend can use them
        result["wordforms"] = wordforms_for_links

    # Add word data only for words tab
    elif purpose == "words":
        from db_models import Wordform

        wordforms = Wordform.get_all_wordforms_for(
            target_language_code=target_language_code,
            sourcefile=sourcefile_entry,
            include_junction_data=True,
        )

        result["wordforms"] = wordforms

    # Add phrase data only for phrases tab
    elif purpose == "phrases":
        from db_models import Phrase

        phrases = Phrase.get_all_phrases_for(
            target_language_code=target_language_code,
            sourcefile=sourcefile_entry,
            include_junction_data=True,
        )

        result["phrases"] = phrases

    # Add image specific data for image tab
    elif purpose == "image":
        # For image tab, we don't need to add additional data
        # The base result already includes filename, sourcefile_type, and other metadata
        # The actual image data is accessed through the view_sourcefile_vw endpoint
        pass

    # Add audio specific data for audio tab
    elif purpose == "audio":
        # For audio tab, we don't need to add additional data
        # The base result already includes filename, sourcefile_type, and other metadata
        # The actual audio data is accessed through the play_sourcefile_audio_vw endpoint
        pass

    return result


def process_sourcefile(
    sourcefile_entry: Sourcefile,
    language_level: LanguageLevel,
    max_new_words: Optional[int],
    max_new_phrases: Optional[int],
    verbose: int = 0,
):
    """
    If MAX_NEW_WORDS or MAX_NEW_PHRASES is 0, skip. If None, then there is no max.

    Now runs synchronously (blocking) instead of asynchronously.
    """
    already_text = bool(sourcefile_entry.text_target)
    sourcefile_entry = ensure_text_extracted(sourcefile_entry)

    # Run translation synchronously
    sourcefile_entry = ensure_translation(sourcefile_entry)

    # Run wordform extraction synchronously
    ensure_tricky_wordforms(
        sourcefile_entry,
        language_level=language_level,
        max_new_words=max_new_words,
    )

    # Run phrase extraction synchronously
    ensure_tricky_phrases(
        sourcefile_entry,
        language_level=language_level,
        max_new_phrases=max_new_phrases,
        verbose=verbose,
    )


def get_incomplete_lemmas_for_sourcefile(sourcefile_entry):
    """Get all incomplete lemmas associated with a sourcefile.

    Returns a list of lemma objects that need their metadata completed.

    Args:
        sourcefile_entry: Sourcefile object to find lemmas for

    Returns:
        List of lemma objects that are incomplete and need metadata
    """
    # Find all wordforms associated with this sourcefile
    sourcefile_wordforms = SourcefileWordform.select(SourcefileWordform.wordform).where(
        SourcefileWordform.sourcefile == sourcefile_entry
    )

    # Get unique wordform IDs
    wordform_ids = [sw.wordform.id for sw in sourcefile_wordforms]  # type: ignore

    if not wordform_ids:
        return []

    # Get the lemmas from these wordforms that are incomplete
    incomplete_lemmas = (
        Lemma.select(Lemma)
        .join(Wordform)
        .where((Wordform.id.in_(wordform_ids)) & (Lemma.is_complete == False))
        .distinct()
    )

    return list(incomplete_lemmas)


def complete_lemma_metadata(lemma):
    """Complete metadata for a lemma.

    Args:
        lemma: Lemma object to complete metadata for

    Returns:
        Updated lemma object with complete metadata
    """
    if lemma.is_complete:
        return lemma

    target_language_name = get_language_name(lemma.target_language_code)

    # Generate full metadata
    try:
        metadata, _ = metadata_for_lemma_full(
            lemma=lemma.lemma, target_language_name=target_language_name
        )

        # Update lemma with new metadata
        for key, value in metadata.items():
            setattr(lemma, key, value)

        # Mark as complete
        lemma.is_complete = True
        lemma.save()

        return lemma
    except Exception as e:
        raise

    return sourcefile_entry


def _create_text_sourcefile(
    sourcedir_entry: Sourcedir,
    filename: str,
    text_target: str,
    description: Optional[str],
    metadata: Dict[str, Any],
    sourcefile_type: str = "text",
) -> Sourcefile:
    """Helper function to create a text-based Sourcefile.

    Assumes filename does not collide (collision should be checked beforehand if necessary).

    Args:
        sourcedir_entry: The Sourcedir object.
        filename: The filename to use.
        text_target: The text content.
        description: Optional description text.
        metadata: Metadata dictionary.
        sourcefile_type: The type of sourcefile (default: "text").

    Returns:
        The created Sourcefile object.
    """
    # Removed collision check logic for simplicity
    # Caller should handle collision checks if needed

    # Create sourcefile entry
    sourcefile = Sourcefile.create(
        sourcedir=sourcedir_entry,
        filename=filename,
        text_target=text_target,
        text_english="",  # Always initialize empty, populated during processing
        metadata=metadata,
        description=description,
        sourcefile_type=sourcefile_type,
    )

    return sourcefile


def preprocess_html_for_llm(html_content: str) -> str:
    """Pre-process raw HTML to simplify it before sending to LLM.

    Removes common non-content tags like script, style, nav, header, footer, etc.

    Args:
        html_content: Raw HTML string.

    Returns:
        Simplified HTML string.

    Raises:
        Exception: If BeautifulSoup parsing fails.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Tags to remove completely
        tags_to_remove = [
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "aside",
            "form",
            "button",
            "iframe",
            "link",
            "meta",
        ]
        for tag_name in tags_to_remove:
            for tag in soup.find_all(tag_name):
                tag.decompose()  # Remove the tag and its content

        # TODO: Consider removing elements by common ad/menu IDs/classes? (More fragile)
        # Example: for el in soup.find_all(class_=re.compile(r'(ad|banner|menu|sidebar|popup)')): el.decompose()

        # TODO: Consider stripping attributes like class, id, style? (Keep for now)
        simplified_html = str(soup)  # Get the modified HTML as a string
        return simplified_html

    except Exception as e:
        # Re-raise exception to be handled by the caller
        # Include context about the failure
        raise Exception(f"BeautifulSoup HTML pre-processing failed: {str(e)}") from e
