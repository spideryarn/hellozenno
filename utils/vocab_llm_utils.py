import json
from addict import Dict as Addict
from anthropic import Anthropic
from openai import OpenAI
from pprint import pprint
import re
from typing import Any, Optional, Set
import tempfile
import os
from slugify import slugify
from peewee import fn, DoesNotExist

from utils.audio_utils import ensure_audio_data
from gdutils.llm_utils import generate_gpt_from_template
from gdutils.strings import PathOrStr
from utils.env_config import CLAUDE_API_KEY, OPENAI_API_KEY
from utils.lang_utils import get_language_name, get_all_languages, get_language_code
from db_models import (
    Lemma,
    Wordform,
    SourcefileWordform,
    Sourcefile,
    Phrase,
    SourcefilePhrase,
    Sentence,
    LemmaExampleSentence,
    SentenceLemma,
)
from utils.word_utils import normalize_text

IMG_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "heic", "bmp", "tiff", "gif"]

GREEK_WIKTIONARY_FREQUENCY_LIST_URL = (
    "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Modern_Greek/5K_Wordlist"
)

EMPTY_LOGD = {
    "sources": {},
    "words": [],
}

anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def extract_text_from_image(
    image_data: bytes | str,
    target_language_name: str,
    verbose: int = 1,
) -> tuple[str, dict]:
    """Extract text from image data.

    Args:
        image_data: Raw image data bytes or path to image file
        target_language_name: Full name of target language (e.g. "Greek")
        verbose: Verbosity level

    Returns:
        Tuple of (extracted_text, extra_info)
    """
    # If image_data is bytes, create a temporary file
    temp_file = None
    try:
        if isinstance(image_data, bytes):
            temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_file.write(image_data)
            temp_file.flush()
            image_filen = temp_file.name
        else:
            image_filen = str(image_data)  # Ensure string type

        txt_tgt, extra = generate_gpt_from_template(
            client=anthropic_client,
            prompt_template_var="extract_text_from_image",
            context_d={"target_language_name": target_language_name},
            response_json=False,
            image_filens=image_filen,  # Now guaranteed to be str
            verbose=verbose - 1,
        )

        assert isinstance(txt_tgt, str), f"Expected str, got {type(txt_tgt)}"
        if verbose >= 1:
            print(f"Extracted text from image -> {txt_tgt[:20]}...")
        if verbose >= 2:
            print(txt_tgt)
        extra = {
            "txt_tgt": txt_tgt,
            "orig": target_language_name,
            "source_type": "image",
            "function": "extract_text_from_image",
            "llm_extra": extra,
        }
        return txt_tgt, extra
    finally:
        if temp_file:
            try:
                os.unlink(temp_file.name)  # Clean up temporary file
            except:
                pass  # Ignore cleanup errors


def translate_to_english(inp: str, source_language_name: str, verbose: int = 1):
    """Translate text to English.

    Args:
        inp: Text to translate
        source_language_name: Full name of source language (e.g. "Greek")
        verbose: Verbosity level

    Returns:
        Tuple of (translated_text, extra_info)
    """
    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template_var="translate_to_english",
        context_d={"txt_tgt": inp, "target_language_name": source_language_name},
        response_json=False,
        verbose=verbose - 1,
    )
    assert isinstance(out, str), f"Expected str, got {type(out)}"
    if verbose >= 1:
        print(
            f"Translated {source_language_name} to English: {inp[:20]} -> {out[:20]}..."
        )
    return out, extra


def translate_from_english(inp: str, target_language: str, verbose: int = 1):
    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template_var="translate_from_english",
        context_d={"txt_en": inp},
        response_json=False,
        verbose=verbose - 1,
    )
    assert isinstance(out, str), f"Expected str, got {type(out)}"
    if verbose >= 1:
        print(f"Translated English to {target_language}: {inp[:20]} -> {out[:20]}...")
    return out, extra


def extract_tricky_words_or_phrases(
    txt: str,
    target_language_name: str,
    language_level: Optional[str] = None,
    ignore_words: list[str] | None = None,
    verbose: int = 1,
):
    """Extract tricky words from text, optionally ignoring already identified words.

    Args:
        txt: Text to analyze in target language
        target_language_name: Full name of target language (e.g. "Greek")
        language_level: Optional language level (e.g. "intermediate")
        ignore_words: Optional list of words to ignore
        verbose: Verbosity level

    Returns:
        Tuple of (tricky_words_dict, extra_info)
    """
    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template_var="extract_tricky_wordforms",
        context_d={
            "txt_tgt": txt,
            "target_language_name": target_language_name,
            "language_level": language_level,
            "ignore_words": ignore_words or [],
        },
        response_json=True,
        verbose=verbose,
    )

    if verbose >= 1:
        print(f"Found {len(out.get('wordforms', []))} new tricky words/phrases")  # type: ignore

    return out, extra  # type: ignore


def process_img_filen(
    image_data: bytes | str,  # Can be raw bytes or a filename
    target_language_name: str,
    should_translate: bool = True,
    should_mp3: bool = False,
    should_add_delays: bool = True,
    ignore_words: Optional[list[str]] = None,
    sourcefile_entry: Optional[
        Sourcefile
    ] = None,  # Optional sourcefile entry for creating SourcefileWordform entries
    verbose: int = 1,
) -> tuple[dict, list, dict]:
    """Process image data to extract and analyze text.

    Args:
        image_data: Raw image data bytes or path to image file
        target_language_name: Full name of target language (e.g. "Greek")
        should_translate: Whether to translate the text
        should_mp3: Whether to generate audio (currently disabled)
        should_add_delays: Whether to add delays between sentences in audio
        ignore_words: List of words to ignore when finding tricky words
        sourcefile_entry: Optional sourcefile entry for creating SourcefileWordform entries
        verbose: Verbosity level

    Returns:
        Tuple of (source_info, tricky_words, extra_info)
    """
    extra = locals()
    if verbose > 1:
        if isinstance(image_data, bytes):
            print(f"Processing image data of length {len(image_data)} bytes")
        else:
            print(f"Processing image file: {image_data}")

    # Extract text from image
    txt_tgt, _ = extract_text_from_image(image_data, target_language_name, verbose=1)
    txt_en = ""

    if should_translate:
        txt_en, _ = translate_to_english(txt_tgt, target_language_name, verbose=1)

    if should_mp3:
        # Create a temporary directory for audio files
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Generate audio data
            audio_data = ensure_audio_data(
                text=txt_tgt,
                should_add_delays=True,
                should_play=False,
                verbose=1,
            )

            # Create sourcefile entry to store the audio
            sourcefile = Sourcefile.create(
                sourcedir=None,  # No sourcedir needed for temporary files
                filename=os.path.basename(txt_tgt),
                audio_filename=os.path.join(tmp_dir, f"{slugify(txt_tgt)}.mp3"),
                text_target=txt_tgt,
                text_english="",
                metadata={},
                sourcefile_type="text",
                audio_data=audio_data,
            )
            txt_tgt_mp3_filen = sourcefile.audio_filename

    tricky_d_orig, _ = extract_tricky_words_or_phrases(
        txt_tgt, target_language_name, ignore_words=ignore_words, verbose=1
    )
    tricky_ad = Addict(tricky_d_orig)
    tricky_words_d = tricky_ad.wordforms

    # Get language code for database
    target_language_code = get_language_code(target_language_name)

    # Process each word and create database entries
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
            wordform=word_d.wordform,
            language_code=target_language_code,
            defaults={
                "lemma_entry": lemma,
                "part_of_speech": word_d.part_of_speech,
                "translations": word_d.translations,
                "inflection_type": word_d.inflection_type,
                "is_lemma": word_d.wordform == word_d.lemma,
            },
        )

        # Create SourcefileWordform entry if we have a sourcefile
        if sourcefile_entry is not None:
            SourcefileWordform.get_or_create(
                sourcefile=sourcefile_entry,
                wordform=wordform,
                defaults={
                    "centrality": word_d.centrality,
                    "ordering": word_counter + 1,
                },
            )

        # Add ordering to the word data for display
        word_d.ordering = word_counter + 1

    # Process phrases
    if sourcefile_entry is not None:
        process_phrases_from_text(
            txt_tgt,
            target_language_name,
            target_language_code,
            sourcefile_entry,
            verbose=1,
        )

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
    if should_mp3:
        source["txt_tgt_mp3_filen"] = str(txt_tgt_mp3_filen)

    return source, tricky_words_d, extra


def metadata_for_lemma_full(
    lemma: str,
    target_language_name: str,
    *,
    verbose: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Get full metadata for a lemma, including translations, etymology, etc.

    Args:
        lemma: The dictionary form of the word
        target_language_name: The full name of the target language (e.g. "Greek")
        verbose: Verbosity level

    Returns:
        Tuple of (metadata, extra_info)
    """
    print(f"LLM-generating metadata for lemma {lemma}")
    # Generate metadata using GPT
    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template_var="metadata_for_lemma",
        context_d={
            "lemma": lemma,
            "target_language_name": target_language_name,
        },
        response_json=True,
        verbose=verbose,
    )

    # Add default values for required fields if missing
    if isinstance(out, dict):
        defaults = {
            "lemma": lemma,  # Ensure lemma is always set
            "synonyms": [],
            "antonyms": [],
            "related_words_phrases_idioms": [],
            "example_usage": [],
            "easily_confused_with": [],
            "mnemonics": [],
            "translations": [],
            "register": "neutral",
            "commonality": 0.5,
            "guessability": 0.5,
            "cultural_context": "",
            "etymology": "",
            "part_of_speech": "unknown",
            "example_wordforms": [lemma],  # Include at least the lemma itself
        }

        for key, default_value in defaults.items():
            if key not in out or out[key] is None:
                out[key] = default_value

        # Create sentence records for example usage
        target_language_code = get_language_code(target_language_name)
        example_usage = out.get("example_usage", [])

        # Get or create the lemma record first
        lemma_model, _ = Lemma.get_or_create(
            lemma=lemma,
            language_code=target_language_code,
            defaults={
                "part_of_speech": out.get("part_of_speech", "unknown"),
                "translations": out.get("translations", []),
            },
        )

        # Process each example sentence
        for example in example_usage:
            if not example.get("phrase") or not example.get("translation"):
                continue

            # First generate the slug to use in get_or_create
            slug = slugify(example["phrase"])
            if len(slug) > 255:
                slug = slug[:255]

            # Create sentence if it doesn't exist or update if it does
            sentence, created = Sentence.update_or_create(
                lookup={
                    "language_code": target_language_code,
                    "sentence": example["phrase"],
                },
                updates={
                    "translation": example["translation"],
                    "slug": slug,
                },
            )

            # Create both the example sentence link and the lemma-sentence relationship
            LemmaExampleSentence.update_or_create(
                lookup={"lemma": lemma_model, "sentence": sentence}, updates={}
            )
            SentenceLemma.update_or_create(
                lookup={"lemma": lemma_model, "sentence": sentence}, updates={}
            )

        if verbose >= 1:
            # pprint(out, sort_dicts=False)
            print(f"Generated metadata for lemma {lemma}")
        return out, extra

    return {}, {"error": "Invalid response format"}


def quick_search_for_wordform(
    wordform: str, target_language_code: str, verbose: int = 1
) -> tuple[dict, dict]:
    """Look up a wordform and return its dictionary entry.

    Args:
        wordform: The word form to look up
        target_language_code: ISO language code (e.g. 'el' for Greek)
        verbose: Verbosity level for logging

    Returns:
        Tuple of (word_metadata, extra_info) where word_metadata follows this schema:
        {
            "wordform": Optional[str],  # the sanitized form if valid, None if invalid
            "lemma": Optional[str],  # the dictionary form this belongs to, None if invalid
            "part_of_speech": Optional[str],  # e.g. "verb", "adjective", "noun", etc.
            "translations": Optional[list[str]],  # English translations
            "inflection_type": Optional[str],  # e.g. "first-person singular present"
            "possible_misspellings": Optional[list[str]]  # ordered list of corrections, or None if valid
        }

    Raises:
        ValueError: If the input parameters are invalid (empty, wrong type)
        LookupError: If the language code is not found
    """
    # Input validation
    if not isinstance(wordform, str) or not isinstance(target_language_code, str):
        raise ValueError("wordform and target_language_code must be strings")

    wordform, target_language_code = wordform.strip(), target_language_code.strip()
    if not wordform or not target_language_code:
        raise ValueError("wordform and target_language_code cannot be empty")

    target_language_name = get_language_name(target_language_code)

    # Try up to 3 times to get a valid JSON response
    max_retries = 3
    last_error = None
    for attempt in range(max_retries):
        try:
            out, extra = generate_gpt_from_template(
                client=anthropic_client,
                prompt_template_var="quick_search_for_wordform",
                context_d={
                    "wordform": wordform,
                    "target_language_name": target_language_name,
                },
                response_json=True,
                verbose=verbose,
            )

            if not out or not isinstance(out, dict):
                if attempt < max_retries - 1:
                    continue
                # If all retries failed, return a default response
                out = {
                    "wordform": None,
                    "lemma": None,
                    "part_of_speech": None,
                    "translations": None,
                    "inflection_type": None,
                    "possible_misspellings": None,
                }
                return out, {"error": "Invalid response format"}

            # Ensure all required fields are present
            required_fields = {
                "wordform": None,
                "lemma": None,
                "part_of_speech": None,
                "translations": None,
                "inflection_type": None,
                "possible_misspellings": None,
            }
            for field, default in required_fields.items():
                if field not in out:
                    out[field] = default

            if verbose >= 1:
                pprint(out, sort_dicts=False)
            return out, extra

        except json.JSONDecodeError as e:
            last_error = e
            if attempt < max_retries - 1:
                continue

    # If all retries failed, return a default response
    out = {
        "wordform": None,
        "lemma": None,
        "part_of_speech": None,
        "translations": None,
        "inflection_type": None,
        "possible_misspellings": None,
    }
    return out, {"error": f"Failed to parse JSON response: {last_error}"}


def extract_phrases_from_text(
    txt: str,
    target_language_name: str,
    language_level: Optional[str] = None,
    verbose: int = 1,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract idiomatic phrases and expressions from text."""
    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template_var="extract_phrases_from_text",
        context_d={
            "txt_tgt": txt,
            "target_language_name": target_language_name,
            "language_level": language_level,
        },
        response_json=True,
        verbose=verbose,
    )

    # Ensure out is a dict
    if not isinstance(out, dict):
        out = {
            "phrases": [],
            "source": {
                "txt_tgt": txt,
            },
        }

    # Add default values for required fields if missing
    defaults = {
        "phrases": [],
        "source": {
            "txt_tgt": txt,
        },
    }

    phrase_defaults = {
        "canonical_form": "",
        "raw_forms": [],
        "translations": [],
        "examples": [],
        "cultural_context": "",
        "register": "neutral",
        "commonality": 0.5,
    }

    for key, default_value in defaults.items():
        if key not in out or out[key] is None:
            out[key] = default_value

    for phrase in out.get("phrases", []):
        for key, default_value in phrase_defaults.items():
            if key not in phrase or phrase[key] is None:
                phrase[key] = default_value

    if verbose >= 1:
        pprint(out, sort_dicts=False)

    return out, extra


def create_interactive_word_links(
    text: str,
    wordforms: list[dict],
    target_language_code: str,
) -> tuple[str, set[str]]:
    """Enhance the input text by wrapping tricky wordforms with HTML links.

    The text will be formatted for readability with:
    - Paragraphs wrapped in <p> tags
    - Lines wrapped at ~65 characters
    - Proper indentation preserved
    - Single newlines converted to <br>

    Returns:
        Tuple of (enhanced_text, found_wordforms) where found_wordforms is a set of
        wordforms that were found in the text
    """
    from utils.store_utils import load_or_generate_lemma_metadata

    # Track which wordforms we actually find in the text
    found_wordforms = set()

    def get_etymology(lemma: str) -> str:
        """Get etymology from lemma metadata."""
        try:
            lemma_metadata = load_or_generate_lemma_metadata(
                lemma=lemma, target_language_code=target_language_code
            )
            return lemma_metadata.get("etymology", "")
        except FileNotFoundError:
            return ""

    def replace_match(match):
        """Replace a matched word with an HTML link."""
        word = match.group(0)  # Original word with case and accents preserved
        normalized_word = normalize_text(word)
        wf = next(
            (
                wf
                for wf in sorted_wordforms
                if normalize_text(wf["wordform"]) == normalized_word
            ),
            None,
        )
        if wf:
            found_wordforms.add(wf["wordform"])  # Track that we found this wordform
            lemma = wf["lemma"]
            translations = wf.get("translations", [])
            if not translations:
                translations = [wf.get("translated_word", "")]
            translation = "; ".join(t for t in translations if t)
            etymology = get_etymology(lemma)
            # Use the original word (with its case) in the link text
            return f'<a target="_blank" href="/el/lemma/{lemma}" class="word-link">{word}</a>'
        return word

    # Sort wordforms by length in descending order to handle overlapping words
    sorted_wordforms = sorted(
        wordforms, key=lambda wf: len(wf["wordform"]), reverse=True
    )

    # Create a regex pattern that matches both original and normalized forms
    pattern_parts = []
    for wf in sorted_wordforms:
        # Add the original form
        pattern_parts.append(re.escape(wf["wordform"]))
        # Add any case variations found in the text
        text_words = re.findall(r"\b\w+\b", text, re.UNICODE)
        for word in text_words:
            if normalize_text(word) == normalize_text(wf["wordform"]):
                pattern_parts.append(re.escape(word))

    # Create the pattern with all variations
    pattern = re.compile(
        r"\b(" + "|".join(set(pattern_parts)) + r")\b",
        re.UNICODE,
    )

    # Split text into paragraphs while preserving all whitespace
    paragraphs = text.split("\n\n")

    # Process each paragraph
    processed_paragraphs = []
    for paragraph in paragraphs:
        if paragraph.strip():  # Only process non-empty paragraphs
            # Process wordforms in this paragraph first
            processed_paragraph = pattern.sub(replace_match, paragraph)

            # Split into lines and wrap long lines
            lines = []
            current_line = []
            current_length = 0

            # Split by whitespace but preserve HTML tags
            tokens = re.split(r"(\s+|<[^>]+>)", processed_paragraph)
            for token in tokens:
                if not token:
                    continue

                # If it's an HTML tag, add it to current line without counting length
                if token.startswith("<"):
                    current_line.append(token)
                # If it's whitespace, add it but don't start a new line
                elif token.isspace():
                    if current_line:
                        current_line.append(token)
                        current_length += len(token)
                # If it's regular text, check length and wrap if needed
                else:
                    if current_length + len(token) > 65:
                        if current_line:
                            lines.append("".join(current_line))
                        current_line = [token]
                        current_length = len(token)
                    else:
                        current_line.append(token)
                        current_length += len(token)

            # Add any remaining content
            if current_line:
                lines.append("".join(current_line))

            # Join lines with <br> and wrap in <p> with proper indentation
            processed_lines = [
                f"    {line.rstrip()}"  # Add 4 spaces indentation for readability
                for line in lines
            ]
            processed_paragraph = "<br>\n".join(processed_lines)
            processed_paragraphs.append(f"<p>\n{processed_paragraph}\n</p>")
        elif paragraph:  # Empty but contains whitespace
            processed_paragraphs.append("<p>&nbsp;</p>")

    # Join all paragraphs with double newlines for spacing
    enhanced_text = "\n\n".join(processed_paragraphs)

    return enhanced_text, found_wordforms


def get_or_create_wordform_metadata(
    wordform: str,
    target_language_code: str,
    verbose: int = 1,
) -> tuple[dict, dict]:
    """
    Get or create metadata for a wordform and its associated lemma.

    This function:
    1. Tries to load existing wordform metadata
    2. If not found, determines/generates the lemma
    3. Gets/generates lemma metadata
    4. Updates wordform metadata with additional info from lemma
    5. Saves the wordform metadata

    Args:
        wordform: The wordform to get/create metadata for
        target_language_code: The language code (e.g. "el" for Greek)
        verbose: Verbosity level for logging

    Returns:
        Tuple of (wordform_metadata, lemma_metadata)
    """
    from utils.store_utils import (
        load_wordform_metadata,
        save_wordform_metadata,
        load_or_generate_lemma_metadata,
        save_lemma_metadata,
        get_lemma_for_wordform,
    )

    # Define the base schema for wordform metadata
    base_wordform_schema = {
        "wordform": wordform,
        "lemma": None,
        "part_of_speech": "unknown",
        "translations": [],
        "inflection_type": "unknown",
        "possible_misspellings": None,
    }

    try:
        # First try to load existing wordform metadata
        wordform_metadata = load_wordform_metadata(wordform, target_language_code)
        lemma = wordform_metadata["lemma"]
    except FileNotFoundError:
        # If not found, we need to determine or generate the lemma
        lemma = get_lemma_for_wordform(
            wordform=wordform, target_language_code=target_language_code
        )

        # Generate new lemma metadata using quick search
        quick_search_result, _ = quick_search_for_wordform(
            wordform, target_language_code=target_language_code
        )

        # If the word is invalid (all fields are None), return the result without saving
        if (
            isinstance(quick_search_result, dict)
            and quick_search_result.get("wordform") is None
            and quick_search_result.get("lemma") is None
        ):
            return quick_search_result, {}

        # Create wordform metadata from quick search result if available
        wordform_metadata = base_wordform_schema.copy()

        # Get lemma from quick search or fall back to wordform
        if isinstance(quick_search_result, dict):
            lemma = quick_search_result.get("lemma", wordform)
            # Update metadata directly from quick search result
            wordform_metadata.update(
                {
                    "lemma": lemma,
                    "part_of_speech": quick_search_result.get(
                        "part_of_speech", "unknown"
                    ),
                    "translations": quick_search_result.get("translations", []),
                    "inflection_type": quick_search_result.get(
                        "inflection_type", "unknown"
                    ),
                    "possible_misspellings": quick_search_result.get(
                        "possible_misspellings"
                    ),
                }
            )
        else:
            lemma = wordform
            wordform_metadata["lemma"] = lemma

    # Get or generate lemma metadata
    try:
        lemma_metadata = load_or_generate_lemma_metadata(
            lemma=lemma, target_language_code=target_language_code
        )
    except FileNotFoundError:
        # Convert code to name for legacy function
        target_language_name = get_language_name(target_language_code)
        lemma_metadata, _ = metadata_for_lemma_full(
            lemma=lemma, target_language_name=target_language_name
        )
        save_lemma_metadata(lemma, lemma_metadata, target_language_name)

    # Update wordform metadata with additional info from lemma if needed
    field_fallbacks = {
        "part_of_speech": "part_of_speech",
        "translations": "translations",
    }
    for target_field, source_field in field_fallbacks.items():
        if (
            target_field not in wordform_metadata
            or not wordform_metadata[target_field]
            or wordform_metadata[target_field] == "unknown"
        ):
            wordform_metadata[target_field] = lemma_metadata.get(
                source_field, base_wordform_schema[target_field]
            )

    # Only save metadata if the word is valid (has a lemma)
    if wordform_metadata["lemma"] is not None:
        save_wordform_metadata(wordform, wordform_metadata, target_language_name)

    return wordform_metadata, lemma_metadata


def extract_tokens(text: Optional[str]) -> Set[str]:
    """Extract unique tokens from text that could be wordforms.

    Handles:
    - Greek characters and diacritics
    - Case-insensitive matching
    - Proper word boundaries
    - Punctuation and whitespace

    Args:
        text: Text to extract tokens from, or None

    Returns:
        Set of unique normalized tokens
    """
    if not text:
        return set()

    # Pattern matches Greek words including accented characters
    # \b ensures we match whole words only
    pattern = r"\b[Α-Ωα-ωίϊΐόάέύϋΰήώ]+\b"

    # Find all matches, convert to lowercase and normalize accents
    tokens = set()
    for token in re.findall(pattern, text):
        # Convert to lowercase
        token = token.lower()
        # Normalize accents by replacing accented characters with their unaccented equivalents
        token = (
            token.replace("ά", "α")
            .replace("έ", "ε")
            .replace("ή", "η")
            .replace("ί", "ι")
            .replace("ό", "ο")
            .replace("ύ", "υ")
            .replace("ώ", "ω")
            .replace("ϊ", "ι")
            .replace("ϋ", "υ")
            .replace("ΐ", "ι")
            .replace("ΰ", "υ")
        )
        tokens.add(token)

    return tokens


def _create_word_link(
    word: str, lemma: str, translation: str = "", etymology: str = ""
) -> str:
    """Create a word link with tooltip data."""
    return f'<a target="_blank" href="/el/lemma/{lemma}" class="word-link">{word}</a>'


def process_phrases_from_text(
    txt: str,
    target_language_name: str,
    target_language_code: str,
    sourcefile_entry=None,
    language_level: Optional[str] = None,
    verbose: int = 1,
) -> list[dict]:
    """Extract and store phrases from text.

    Args:
        txt: Text to analyze
        target_language_name: Full name of target language (e.g. "Greek")
        target_language_code: Language code (e.g. "el")
        sourcefile_entry: Optional sourcefile entry to link phrases to
        language_level: Optional language level
        verbose: Verbosity level

    Returns:
        List of phrase dictionaries
    """
    # Extract phrases
    phrases_d_orig, _ = extract_phrases_from_text(
        txt, target_language_name, language_level, verbose
    )
    phrases_d = phrases_d_orig.get("phrases", [])

    # Process phrases
    for phrase_counter, phrase_d in enumerate(phrases_d):
        # Create or get the phrase
        phrase, phrase_created = Phrase.update_or_create(
            lookup={
                "canonical_form": phrase_d["canonical_form"],
                "language_code": target_language_code,
            },
            updates={
                "raw_forms": phrase_d.get("raw_forms", [phrase_d["canonical_form"]]),
                "translations": phrase_d.get("translations", []),
                "part_of_speech": phrase_d.get("part_of_speech", "phrase"),
                "register": phrase_d.get("register", "neutral"),
                "commonality": phrase_d.get("commonality", 0.5),
                "guessability": phrase_d.get("guessability", 0.5),
                "etymology": phrase_d.get("etymology", ""),
                "cultural_context": phrase_d.get("cultural_context", ""),
                "mnemonics": phrase_d.get("mnemonics", []),
                "component_words": phrase_d.get("component_words", []),
                "usage_notes": phrase_d.get("usage_notes", ""),
                "difficulty_level": phrase_d.get("difficulty_level", "intermediate"),
            },
        )

        # Create SourcefilePhrase entry if we have a sourcefile
        if sourcefile_entry is not None:
            SourcefilePhrase.update_or_create(
                lookup={
                    "sourcefile": sourcefile_entry,
                    "phrase": phrase,
                },
                updates={
                    "centrality": phrase_d.get("centrality", 0.5),
                    "ordering": phrase_counter + 1,
                },
            )

    return phrases_d
