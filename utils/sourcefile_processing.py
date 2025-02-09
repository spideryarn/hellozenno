from pathlib import Path
import tempfile
from gdutils.dt import dt_str
from addict import Addict
import os

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

from config import MAX_IMAGE_SIZE_FOR_STORAGE, MAX_AUDIO_SIZE_FOR_STORAGE
from utils.image_utils import resize_image_to_target_size
from utils.audio_utils import transcribe_audio
from utils.vocab_llm_utils import (
    extract_text_from_image,
    translate_to_english,
    extract_tricky_words_or_phrases,
    extract_phrases_from_text,
    process_phrases_from_text,
)
from db_models import Lemma, Wordform, SourcefileWordform, Phrase, SourcefilePhrase


def process_sourcefile_content(
    sourcefile_entry,
    target_language_name: str,
) -> tuple[dict, list, dict]:
    """Process a sourcefile's content into text, translation, and word data.

    The pipeline is:
    1. Get text (from image/text/audio/etc based on sourcefile_type)
    2. Translate to English
    3. Extract vocabulary and phrases
    4. Create database entries for words and phrases

    Args:
        sourcefile_entry: The Sourcefile model instance to process
        target_language_name: The target language name (not code)

    Returns:
        tuple of (source_dict, tricky_words_list, extra_metadata)
        where source_dict contains txt_tgt, txt_en, etc.
        tricky_words_list contains extracted words data
        and extra_metadata contains any additional metadata
    """
    # 1. Get text based on sourcefile type
    txt_tgt, extra_metadata = get_text_from_sourcefile(
        sourcefile_entry, target_language_name
    )
    if not txt_tgt:
        raise ValueError(f"No text content found in {sourcefile_entry.filename}")

    # 2. Translate to English
    txt_en, _ = translate_to_english(txt_tgt, target_language_name, verbose=1)

    # 3. Extract vocabulary and phrases
    tricky_d_orig, _ = extract_tricky_words_or_phrases(
        txt_tgt, target_language_name, verbose=1
    )
    tricky_ad = Addict(tricky_d_orig)
    tricky_words_d = tricky_ad.wordforms

    # Process words
    target_language_code = sourcefile_entry.sourcedir.language_code
    for word_counter, word_d in enumerate(tricky_words_d):
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
                "ordering": word_counter + 1,
            },
        )

        # Add ordering to word data for display
        word_d.ordering = word_counter + 1

    # Process phrases
    process_phrases_from_text(
        txt_tgt,
        target_language_name,
        target_language_code,
        sourcefile_entry,
        verbose=1,
    )

    # Format word display
    sorted_tricky_words_d = sorted(
        tricky_words_d,
        key=lambda w: w.wordform,
        reverse=True,
    )
    sorted_tricky_words_output = "\n".join(
        [
            f"{word_d.ordering}. {word_d.wordform}-> {', '.join(word_d.translations)}"
            for word_d in sorted_tricky_words_d
        ]
    )

    source = {
        "txt_tgt": txt_tgt,
        "txt_en": txt_en,
        "sorted_words_display": sorted_tricky_words_output,
    }

    return source, tricky_words_d, extra_metadata


def get_text_from_sourcefile(
    sourcefile_entry, target_language_name: str
) -> tuple[str, dict]:
    """Extract text from sourcefile based on its type.

    Args:
        sourcefile_entry: The Sourcefile model instance
        target_language_name: The target language name (not code)

    Returns:
        Tuple of (extracted_text, extra_metadata)

    Raises:
        ValueError: If the sourcefile type is unsupported or content is missing
    """
    if sourcefile_entry.sourcefile_type == "text":
        if not sourcefile_entry.text_target:
            raise ValueError("No text content found")
        return sourcefile_entry.text_target, {}

    elif sourcefile_entry.sourcefile_type == "image":
        if sourcefile_entry.image_data is None:
            raise ValueError("No image data found")

        # Create temp file for image processing
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            temp_file.write(sourcefile_entry.image_data)
            temp_file.flush()
            txt_tgt, extra = extract_text_from_image(
                temp_file.name, target_language_name, verbose=1
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
            language_code = sourcefile_entry.sourcedir.language_code
            txt_tgt, extra = transcribe_audio(Path(temp_file.name), language_code)

            try:
                os.unlink(temp_file.name)  # Clean up temp file
            except:
                pass  # Ignore cleanup errors

            # Add text source to metadata
            extra["text_source"] = "whisper_transcription"
            return txt_tgt, extra

    else:
        raise ValueError(
            f"Unsupported sourcefile type: {sourcefile_entry.sourcefile_type}"
        )


def process_uploaded_file(
    file_content: bytes, original_filename: str, sourcedir_path: str, language_code: str
) -> tuple[bytes, str, dict]:
    """Process an uploaded file, handling resizing and filename generation.

    Args:
        file_content: The raw file content
        original_filename: The original filename
        sourcedir_path: The path of the source directory
        language_code: The language code

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
        filename = f"{dt_str()}_{sourcedir_path}_{language_code}{ext}"
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

    elif ext == ".mp3":
        # For audio, just verify it's a valid MP3 file
        # We could add audio validation here if needed
        if len(file_content) > MAX_AUDIO_SIZE_FOR_STORAGE:
            raise ValueError(
                f"Audio file too large (max {MAX_AUDIO_SIZE_FOR_STORAGE // (1024*1024)}MB)"
            )

    return file_content, filename, metadata
