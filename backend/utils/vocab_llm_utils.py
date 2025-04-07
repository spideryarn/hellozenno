import json
import time
from anthropic import Anthropic
from openai import OpenAI
from pprint import pprint
import re
from typing import Any, Optional
from slugify import slugify

from gjdutils.llm_utils import generate_gpt_from_template
from utils.prompt_utils import get_prompt_template_path
from utils.env_config import CLAUDE_API_KEY, OPENAI_API_KEY
from utils.lang_utils import get_language_name, get_language_code
from db_models import (
    Lemma,
    Phrase,
    SourcefilePhrase,
    Sentence,
    LemmaExampleSentence,
    SentenceLemma,
)


IMG_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "heic", "bmp", "tiff", "gif"]

GREEK_WIKTIONARY_FREQUENCY_LIST_URL = (
    "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Modern_Greek/5K_Wordlist"
)

EMPTY_LOGD = {
    "sources": {},
    "words": [],
}

anthropic_client = Anthropic(api_key=CLAUDE_API_KEY.get_secret_value())
openai_client = OpenAI(api_key=OPENAI_API_KEY.get_secret_value())


def extract_text_from_image(
    image_data: str,  # Path to image file
    target_language_name: str,
    verbose: int = 1,
) -> tuple[str, dict]:
    """Extract text from image data.

    Args:
        image_data: Path to image file
        target_language_name: Full name of target language (e.g. "Greek")
        verbose: Verbosity level

    Returns:
        Tuple of (extracted_text, extra_info)
    """
    txt_tgt, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template=get_prompt_template_path("extract_text_from_image"),
        context_d={"target_language_name": target_language_name},
        response_json=False,
        image_filens=str(image_data),  # Ensure string type
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
        prompt_template=get_prompt_template_path("translate_to_english"),
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
        prompt_template=get_prompt_template_path("translate_from_english"),
        context_d={"txt_en": inp},
        response_json=False,
        verbose=verbose - 1,
    )
    assert isinstance(out, str), f"Expected str, got {type(out)}"
    if verbose >= 1:
        print(f"Translated English to {target_language}: {inp[:20]} -> {out[:20]}...")
    return out, extra


def extract_tricky_words(
    txt: str,
    target_language_name: str,
    language_level: Optional[str] = None,
    max_new_words: Optional[int] = None,
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
    if not txt.strip() or txt.strip() == "-":
        return {}, {}

    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template=get_prompt_template_path("extract_tricky_wordforms"),
        context_d={
            "txt_tgt": txt,
            "target_language_name": target_language_name,
            "language_level": language_level,
            "max_new_words": max_new_words,
            "ignore_words": ignore_words or [],
        },
        response_json=True,
        verbose=verbose,
    )
    assert isinstance(out, dict), f"Expected dict, got {type(out)}"

    if verbose >= 1:
        print(f"Found {len(out.get('wordforms', []))} new tricky words/phrases")  # type: ignore

    return out, extra  # type: ignore


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
    import logging
    logger = logging.getLogger(__name__)
    
    # Use error level to make sure it shows up in logs
    logger.error(f"DEBUG V2: LLM-generating metadata for lemma '{lemma}' in {target_language_name}")
    print(f"DEBUG V2: LLM-generating metadata for lemma '{lemma}' in {target_language_name}")
    
    # Check if API key is properly set
    api_key_value = CLAUDE_API_KEY.get_secret_value()
    api_key_valid = api_key_value and len(api_key_value) > 20
    if not api_key_valid:
        logger.error(f"DEBUG ERROR: Claude API key appears to be invalid or missing!")
        print(f"DEBUG ERROR: Claude API key appears to be invalid or missing!")
    
    try:
        # Generate metadata using Claude
        logger.error(f"DEBUG V2: Calling Claude API with template 'metadata_for_lemma'")
        print(f"DEBUG V2: Calling Claude API with template 'metadata_for_lemma'")
        
        template_path = get_prompt_template_path("metadata_for_lemma")
        logger.error(f"DEBUG V2: Using prompt template at: {template_path}")
        
        try:
            # Try with more debug information
            out, extra = generate_gpt_from_template(
                client=anthropic_client,
                prompt_template=template_path,
                context_d={
                    "lemma": lemma,
                    "target_language_name": target_language_name,
                },
                response_json=True,
                verbose=max(verbose, 1),  # Force verbose mode for debugging
            )
            
            logger.error(f"DEBUG V2: Claude API response received for lemma '{lemma}'")
            logger.error(f"DEBUG V2: Response type: {type(out)}")
            print(f"DEBUG V2: Claude API response received. Response type: {type(out)}")
            
            if isinstance(out, dict):
                # Summarize the response to avoid flooding logs
                field_count = len(out.keys())
                has_translations = "translations" in out and out["translations"]
                logger.error(f"DEBUG V2: Response has {field_count} fields, translations present: {has_translations}")
                print(f"DEBUG V2: Response has {field_count} fields, translations present: {has_translations}")
            else:
                # Log the raw response for debugging
                logger.error(f"DEBUG V2: Raw response (non-dict): {str(out)[:200]}...")
                print(f"DEBUG V2: Raw response (not a dictionary): {str(out)[:100]}...")
        except Exception as api_error:
            # Detailed logging of Claude API errors
            logger.error(f"DEBUG V2: Claude API call failed: {str(api_error)}", exc_info=True)
            print(f"DEBUG V2: Claude API call failed: {str(api_error)}")
            
            # Return a minimal dictionary with the error so we can track it
            return {
                "lemma": lemma,
                "translations": [f"[API Error: {str(api_error)}]"],
                "part_of_speech": "unknown",
                "example_wordforms": [lemma],
                "api_error": True,
            }, {"error": f"Claude API error: {str(api_error)}"}
        
        # Check if output is valid
        if not isinstance(out, dict):
            logger.error(f"DEBUG V2: Claude API returned invalid format for lemma '{lemma}': {type(out)}")
            logger.error(f"DEBUG V2: Raw response: {str(out)[:500]}...")
            print(f"DEBUG V2: Claude API returned invalid format: {type(out)}")
            
            # Try to recover by creating a minimal valid dictionary
            minimal_data = {
                "lemma": lemma,
                "translations": ["[Response format error]"],
                "part_of_speech": "unknown",
                "example_wordforms": [lemma],
                "format_error": True,
            }
            return minimal_data, {"error": f"Invalid response format: {type(out)}", "raw_response": str(out)}

        # Add default values for required fields if missing
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
                logger.error(f"DEBUG V2: Adding default value for missing field '{key}' in lemma '{lemma}'")
                out[key] = default_value

        try:
            # Create sentence records for example usage
            target_language_code = get_language_code(target_language_name)
            example_usage = out.get("example_usage", [])
            logger.error(f"DEBUG V2: Processing {len(example_usage)} example sentences for lemma '{lemma}'")

            # Get or create the lemma record first
            try:
                logger.error(f"DEBUG V2: Creating lemma record in database for '{lemma}'")
                lemma_model, created = Lemma.get_or_create(
                    lemma=lemma,
                    language_code=target_language_code,
                    defaults={
                        "part_of_speech": out.get("part_of_speech", "unknown"),
                        "translations": out.get("translations", []),
                        "is_complete": True,  # Mark as complete to prevent regeneration attempts
                    },
                )
                
                # Add all metadata fields to the lemma model
                for key, value in out.items():
                    setattr(lemma_model, key, value)
                
                # Save the updated model
                lemma_model.save()
                
                logger.error(f"DEBUG V2: Lemma record {'created' if created else 'found and updated'} in database")
                print(f"DEBUG V2: Lemma record {'created' if created else 'found and updated'} in database")
            except Exception as db_error:
                logger.error(f"DEBUG V2: Error saving lemma to database: {str(db_error)}", exc_info=True)
                print(f"DEBUG V2: Error saving lemma to database: {str(db_error)}")
                # Continue processing without failing

            # Process each example sentence
            for i, example in enumerate(example_usage):
                if not example.get("phrase") or not example.get("translation"):
                    logger.error(f"DEBUG V2: Skipping example {i+1} due to missing phrase or translation")
                    continue

                try:
                    # First generate the slug to use in get_or_create
                    phrase = example["phrase"]
                    slug = slugify(phrase)
                    if len(slug) > 255:
                        slug = slug[:255]

                    logger.error(f"DEBUG V2: Creating sentence: '{phrase[:30]}...'")
                    
                    # Create sentence if it doesn't exist or update if it does
                    sentence, created = Sentence.update_or_create(
                        lookup={
                            "language_code": target_language_code,
                            "sentence": phrase,
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
                    logger.error(f"DEBUG V2: Example sentence {i+1} processed successfully")
                except Exception as sentence_error:
                    logger.error(f"DEBUG V2: Error processing example sentence {i+1}: {str(sentence_error)}")
                    # Continue processing other sentences
                    continue
        except Exception as e:
            logger.error(f"DEBUG V2: Error processing database updates for lemma '{lemma}': {str(e)}", exc_info=True)
            print(f"DEBUG V2: Error processing database updates: {str(e)}")
            # We'll still return the metadata even if database updates fail

        # Final check - verify lemma is in database
        lemma_exists = Lemma.select().where(
            Lemma.lemma == lemma,
            Lemma.language_code == target_language_code
        ).exists()
        
        logger.error(f"DEBUG V2: Final check - lemma exists in database: {lemma_exists}")
        print(f"DEBUG V2: Final check - lemma exists in database: {lemma_exists}")
        
        if verbose >= 1:
            logger.error(f"DEBUG V2: Generated metadata for lemma '{lemma}'")
        
        # Add debug info to the output
        out["_debug_info"] = {
            "saved_to_db": lemma_exists,
            "timestamp": time.time(),
        }
        
        return out, extra

    except Exception as e:
        logger.error(f"DEBUG V2: Error generating metadata for lemma '{lemma}': {str(e)}", exc_info=True)
        print(f"DEBUG V2: Error generating metadata: {str(e)}")
        
        # Return a minimal dictionary with the error information
        return {
            "lemma": lemma,
            "translations": [f"[Generation Error: {str(e)}]"],
            "part_of_speech": "unknown",
            "example_wordforms": [lemma],
            "_debug_info": {
                "error": str(e),
                "timestamp": time.time(),
            }
        }, {"error": f"Exception during metadata generation: {str(e)}"}


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
                prompt_template=get_prompt_template_path("quick_search_for_wordform"),
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
    max_new_phrases: Optional[int] = None,
    verbose: int = 1,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract idiomatic phrases and expressions from text."""
    if not txt.strip() or txt.strip() == "-":
        return {}, {}

    out, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template=get_prompt_template_path("extract_phrases_from_text"),
        context_d={
            "txt_tgt": txt,
            "target_language_name": target_language_name,
            "language_level": language_level,
            "max_new_phrases": max_new_phrases,
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
        "literal_translation": "",
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


def create_interactive_word_data(
    text: str,
    wordforms: list[dict],
    target_language_code: str,
) -> tuple[list[dict], set[str]]:
    """Analyze the input text and return structured data about recognized words.
    
    Instead of generating HTML, this function returns structured data that can be
    used by the frontend to render the text with interactive elements.
    
    Returns:
        Tuple of (recognized_words, found_wordforms) where:
        - recognized_words is a list of dictionaries, each containing information about a recognized word:
          {
            "word": str,             # The exact word as it appears in the text
            "start": int,            # Character position where the word starts
            "end": int,              # Character position where the word ends
            "lemma": str,            # The dictionary form of the word
            "translations": list,    # List of English translations
            "part_of_speech": str,   # Part of speech (noun, verb, etc.)
            "inflection_type": str,  # Grammatical form (e.g., "past tense")
          }
        - found_wordforms is a set of wordforms that were found in the text
    """
    from utils.store_utils import load_or_generate_lemma_metadata
    from utils.word_utils import ensure_nfc, normalize_text
    
    # Track which wordforms we actually find in the text
    found_wordforms = set()
    recognized_words = []
    
    # Sort wordforms by length in descending order to handle overlapping words
    sorted_wordforms = sorted(
        wordforms, key=lambda wf: len(wf["wordform"]), reverse=True
    )

    # First, normalize the input text to NFC for consistent pattern matching
    text_nfc = ensure_nfc(text)
    
    # Create a regex pattern that matches both original and normalized forms
    pattern_parts = []
    wordform_variations = {}  # Map normalized forms to their variations
    
    for wf in sorted_wordforms:
        # Ensure wordform is in NFC form for consistent pattern matching
        nfc_wordform = ensure_nfc(wf["wordform"])
        normalized_form = normalize_text(nfc_wordform)
        
        # Initialize the variations set if we haven't seen this normalized form before
        if normalized_form not in wordform_variations:
            wordform_variations[normalized_form] = {
                "original_wordform": wf["wordform"],
                "variations": set(),
                "metadata": wf
            }
        
        # Add the original form to the variations
        wordform_variations[normalized_form]["variations"].add(nfc_wordform)
        pattern_parts.append(re.escape(nfc_wordform))
        
        # Add any case variations found in the text
        text_words = re.findall(r"\b\w+\b", text_nfc, re.UNICODE)
        for word in text_words:
            # Ensure word is in NFC form before comparison
            nfc_word = ensure_nfc(word)
            if normalize_text(nfc_word) == normalized_form:
                wordform_variations[normalized_form]["variations"].add(nfc_word)
                pattern_parts.append(re.escape(nfc_word))
    
    # If no pattern parts, return empty results
    if not pattern_parts:
        return [], set()
    
    # Create the pattern with all unique variations
    pattern = re.compile(
        r"\b(" + "|".join(set(pattern_parts)) + r")\b",
        re.UNICODE,
    )
    
    # Find all matches in the text
    for match in pattern.finditer(text_nfc):
        word = match.group(0)  # Original word with case and accents preserved
        start_pos = match.start()
        end_pos = match.end()
        
        # First ensure the word is in NFC form for consistent matching
        word_nfc = ensure_nfc(word)
        normalized_word = normalize_text(word_nfc)
        
        # Find which wordform this matches
        for norm_form, data in wordform_variations.items():
            if any(normalize_text(var) == normalized_word for var in data["variations"]):
                wf = data["metadata"]
                found_wordforms.add(wf["wordform"])  # Track that we found this wordform
                
                # Gather word data
                lemma = wf["lemma"]
                translations = wf.get("translations", [])
                if not translations and wf.get("translated_word"):
                    translations = [wf.get("translated_word")]
                
                # Add this word occurrence to our results
                recognized_words.append({
                    "word": word,                             # Original word from text
                    "start": start_pos,                       # Position in text
                    "end": end_pos,                           # End position in text
                    "lemma": lemma,                           # Dictionary form
                    "translations": translations,             # English meanings
                    "part_of_speech": wf.get("part_of_speech", "unknown"),  # Noun, verb, etc
                    "inflection_type": wf.get("inflection_type", "unknown") # Grammatical form
                })
                break
    
    # Sort recognized words by their position in the text
    recognized_words.sort(key=lambda w: w["start"])
    
    return recognized_words, found_wordforms


# DEPRECATED: This function is maintained only for backward compatibility.
# New code should use create_interactive_word_data() instead which returns structured
# data rather than HTML. This provides better separation of concerns between
# backend (data processing) and frontend (rendering).
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
    from utils.word_utils import ensure_nfc, normalize_text
    from flask import url_for
    from utils.url_registry import endpoint_for

    # Import the wordform view function for url_for
    from views.wordform_views import get_wordform_metadata_vw

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
        # First ensure the word is in NFC form for consistent matching
        word_nfc = ensure_nfc(word)
        normalized_word = normalize_text(word_nfc)
        wf = next(
            (
                wf
                for wf in sorted_wordforms
                if normalize_text(ensure_nfc(wf["wordform"])) == normalized_word
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
            wordform_url = url_for(
                endpoint_for(get_wordform_metadata_vw),
                target_language_code=target_language_code,
                wordform=wf["wordform"],  # Link to the wordform instead of lemma
                _external=False,
            )
            return f'<a href="{wordform_url}" class="word-link">{word}</a>'
        return word

    # Sort wordforms by length in descending order to handle overlapping words
    sorted_wordforms = sorted(
        wordforms, key=lambda wf: len(wf["wordform"]), reverse=True
    )

    # First, normalize the input text to NFC for consistent pattern matching
    text_nfc = ensure_nfc(text)

    # Create a regex pattern that matches both original and normalized forms
    pattern_parts = []
    for wf in sorted_wordforms:
        # Ensure wordform is in NFC form for consistent pattern matching
        nfc_wordform = ensure_nfc(wf["wordform"])
        # Add the original form
        pattern_parts.append(re.escape(nfc_wordform))
        # Add any case variations found in the text
        text_words = re.findall(r"\b\w+\b", text_nfc, re.UNICODE)
        for word in text_words:
            # Ensure word is in NFC form before comparison
            nfc_word = ensure_nfc(word)
            if normalize_text(nfc_word) == normalize_text(nfc_wordform):
                pattern_parts.append(re.escape(nfc_word))

    # Create the pattern with all variations
    pattern = re.compile(
        r"\b(" + "|".join(set(pattern_parts)) + r")\b",
        re.UNICODE,
    )

    # Split text into paragraphs while preserving all whitespace
    paragraphs = text_nfc.split("\n\n")

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


def extract_tokens(text: Optional[str]) -> set[str]:
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


def process_phrases_from_text(
    txt: str,
    target_language_name: str,
    target_language_code: str,
    language_level: Optional[str],
    max_new_phrases: Optional[int],
    sourcefile_entry=None,
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
        txt, target_language_name, language_level, max_new_phrases
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
                "literal_translation": phrase_d.get("literal_translation", ""),
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
