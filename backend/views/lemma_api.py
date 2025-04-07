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
    
    If the lemma doesn't exist, it will be generated using Claude AI.
    """
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)
    
    try:
        # First try to find the lemma in the database
        lemma_model = (
            Lemma.select()
            .where(
                Lemma.lemma == lemma,
                Lemma.language_code == target_language_code,
            )
            .join(LemmaExampleSentence, JOIN.LEFT_OUTER)
            .get()
        )
        
        # Load or regenerate metadata if incomplete
        lemma_data = load_or_generate_lemma_metadata(
            lemma=lemma,
            target_language_code=target_language_code,
            generate_if_incomplete=True,
        )
        
        # All required fields should be handled by load_or_generate_lemma_metadata

        # Create the response
        response_data = {
            "lemma_metadata": lemma_data,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "metadata": {
                "created_at": lemma_model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": lemma_model.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
        return jsonify(response_data)
        
    except DoesNotExist:
        # Lemma not found, generate new metadata
        try:
            # This will create the lemma in the database
            lemma_data = load_or_generate_lemma_metadata(
                lemma=lemma,
                target_language_code=target_language_code,
                generate_if_incomplete=True,
            )
            
            # Find the newly created lemma
            lemma_model = Lemma.get(
                Lemma.lemma == lemma,
                Lemma.language_code == target_language_code,
            )
            
            # Create the response
            response_data = {
                "lemma_metadata": lemma_data,
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
                "metadata": {
                    "created_at": lemma_model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": lemma_model.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
            return jsonify(response_data)
            
        except Exception as e:
            # If generation fails, return a proper 500 error
            error_data = {
                "error": "Failed to generate lemma",
                "description": f"Could not generate metadata for lemma '{lemma}': {str(e)}",
                "target_language_code": target_language_code,
                "target_language_name": get_language_name(target_language_code),
            }
            response = jsonify(error_data)
            response.status_code = 500
            return response
