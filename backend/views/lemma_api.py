"""API endpoints for lemmas.

All endpoints for interacting with lemmas programmatically.
These endpoints follow the standard pattern:
/api/lang/lemma/...
"""

from flask import Blueprint, jsonify, request
from peewee import DoesNotExist, JOIN
import time
import logging
import urllib.parse

from utils.lang_utils import get_language_name
from db_models import Lemma, LemmaExampleSentence
from utils.store_utils import load_or_generate_lemma_metadata

# Create a blueprint with standardized prefix
lemma_api_bp = Blueprint("lemma_api", __name__, url_prefix="/api/lang/lemma")

logger = logging.getLogger(__name__)


@lemma_api_bp.route("/<target_language_code>/<lemma>/data")
def get_lemma_data_api(target_language_code: str, lemma: str):
    """Get detailed data for a specific lemma."""
    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma) & (Lemma.language_code == target_language_code)
        )
        data = lemma_model.to_dict()
        return jsonify(data)
    except DoesNotExist:
        response = jsonify(
            {"error": "Not Found", "description": f"Lemma '{lemma}' not found"}
        )
        response.status_code = 404
        return response


@lemma_api_bp.route("/<target_language_code>/lemmas")
def lemmas_list_api(target_language_code: str):
    """Get all lemmas for a language.

    Returns a list of all lemmas for the specified language code.
    Supports sorting via the 'sort' query parameter:
    - 'alpha' (default): Sort alphabetically
    - 'date': Sort by last updated date
    - 'commonality': Sort by commonality score
    """
    # Get sort parameter from request
    sort = request.args.get("sort", "alpha")

    # Get all lemmas for this language from the database
    lemmas = Lemma.get_all_lemmas_for(language_code=target_language_code, sort_by=sort)

    # Transform the response to match the frontend's expected format
    lemma_list = []
    for lemma_obj in lemmas:
        lemma_data = lemma_obj.to_dict()
        # Add any additional fields the frontend might need
        lemma_list.append(lemma_data)

    return jsonify(lemma_list)


@lemma_api_bp.route("/<target_language_code>/lemma/<lemma>/metadata")
def get_lemma_metadata_api(target_language_code: str, lemma: str):
    """Get detailed metadata for a lemma.

    This API endpoint corresponds to the get_lemma_metadata_vw view function.
    It returns complete metadata for a lemma, including default values for missing fields.
    """
    # Add a flag to help us diagnose if code changes are being applied
    logger.error(f"DEBUG: NEW LEMMA CODE PATH - Version 2 - get_lemma_metadata_api called for '{lemma}' in {target_language_code}")
    print(f"DEBUG: NEW LEMMA CODE PATH - Version 2 - get_lemma_metadata_api called for '{lemma}' in {target_language_code}")
    
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)
    logger.info(f"get_lemma_metadata_api called for lemma: '{lemma}' in language: {target_language_code}")

    # First, check if the lemma exists in the database to diagnose potential issues
    lemma_exists = Lemma.select().where(
        Lemma.lemma == lemma,
        Lemma.language_code == target_language_code
    ).exists()
    
    if not lemma_exists:
        logger.error(f"DEBUG: Lemma '{lemma}' does NOT exist in database - will proceed to generation")
    else:
        logger.error(f"DEBUG: Lemma '{lemma}' EXISTS in database! This contradicts our Supabase check.")
    
    start_time = time.time()
    try:
        # Time the database fetch with prefetch
        fetch_start = time.time()
        lemma_model = (
            Lemma.select()
            .where(
                Lemma.lemma == lemma,
                Lemma.language_code == target_language_code,
            )
            .join(LemmaExampleSentence, JOIN.LEFT_OUTER)
            .get()
        )
        fetch_time = time.time() - fetch_start
        logger.info(f"Fetched lemma with joins in {fetch_time:.2f}s")

        # Load metadata, checking completeness
        dict_start = time.time()
        lemma_data = load_or_generate_lemma_metadata(
            lemma=lemma,
            target_language_code=target_language_code,
            generate_if_incomplete=True,
        )
        dict_time = time.time() - dict_start
        logger.info(f"Loaded/generated metadata in {dict_time:.2f}s")

        # Ensure all required fields are present with defaults
        default_easily_confused = [
            {
                "lemma": "",
                "explanation": "",
                "example_usage_this_target": "",
                "example_usage_this_source": "",
                "example_usage_other_target": "",
                "example_usage_other_source": "",
                "mnemonic": "",
                "notes": "",
            }
        ]

        required_fields = {
            "translations": [],
            "etymology": "",
            "commonality": 0.0,
            "guessability": 0.0,
            "register": "",
            "example_usage": [],
            "mnemonics": [],
            "related_words_phrases_idioms": [],
            "synonyms": [],
            "antonyms": [],
            "example_wordforms": [],
            "cultural_context": "",
            "easily_confused_with": default_easily_confused,
        }

        # Add any missing fields with default values
        for field, default in required_fields.items():
            if field not in lemma_data or lemma_data[field] is None:
                lemma_data[field] = default
            elif field == "easily_confused_with" and lemma_data[field]:
                # Keep existing easily_confused_with if it exists
                continue

        # Add metadata for the response
        response_data = {
            "lemma_metadata": lemma_data,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "metadata": {
                "created_at": lemma_model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": lemma_model.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "debug_info": "The lemma was found in the database and loaded successfully",
        }

        logger.info(f"Successfully returned lemma metadata for '{lemma}'")
        return jsonify(response_data)
    except DoesNotExist:
        logger.error(f"Lemma '{lemma}' not found in database. Should be generating it...")
        try:
            # Try to generate the lemma even though it doesn't exist
            dict_start = time.time()
            logger.error(f"Attempting to generate lemma metadata for '{lemma}'")
            lemma_data = load_or_generate_lemma_metadata(
                lemma=lemma,
                target_language_code=target_language_code,
                generate_if_incomplete=True,
            )
            dict_time = time.time() - dict_start
            logger.error(f"Generated new lemma metadata in {dict_time:.2f}s")
            
            # After generation, check again if it made it to the database
            lemma_exists = Lemma.select().where(
                Lemma.lemma == lemma,
                Lemma.language_code == target_language_code
            ).exists()
            
            db_status = "Saved successfully to database" if lemma_exists else "FAILED to save to database!"
            logger.error(f"After generation, lemma database status: {db_status}")
            
            # Create a response with the generated data
            response_data = {
                "lemma_metadata": lemma_data,
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
                "metadata": {
                    "created_at": "just now",
                    "updated_at": "just now",
                },
                "debug_info": f"The lemma was newly generated. Database status: {db_status}"
            }
            
            # Force successful response even if there's an issue
            return jsonify(response_data)
        except Exception as e:
            # Log the detailed error if lemma generation fails
            logger.error(f"Failed to generate lemma '{lemma}': {str(e)}", exc_info=True)
            
            # Instead of failing with an error, return a placeholder lemma with debug info
            # This will prevent 500 errors in production while we investigate
            placeholder_lemma = {
                "lemma": lemma,
                "translations": [f"[Auto-generation failed: {str(e)}]"],
                "etymology": "Generation failed, please try again later",
                "commonality": 0.5,
                "guessability": 0.5,
                "register": "neutral",
                "example_usage": [],
                "mnemonics": [],
                "related_words_phrases_idioms": [],
                "synonyms": [],
                "antonyms": [],
                "example_wordforms": [lemma],
                "cultural_context": "",
                "is_complete": False,
                "part_of_speech": "unknown",
                "notes": f"Error during generation: {str(e)}"
            }
            
            response_data = {
                "lemma_metadata": placeholder_lemma,
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
                "metadata": {
                    "created_at": "error",
                    "updated_at": "error",
                },
                "debug_info": f"Lemma generation failed with error: {str(e)}"
            }
            
            return jsonify(response_data)
            
        # This code should never be reached if we properly handle the generation attempt
        response_data = {
            "error": "Not Found",
            "description": f"Lemma '{lemma}' not found",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
        }
        response = jsonify(response_data)
        response.status_code = 404
        return response
