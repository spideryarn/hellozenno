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
from utils.sourcefile_utils import complete_lemma_metadata

# Import the auth decorators and the new exception
from utils.auth_utils import api_auth_required, api_auth_optional
from utils.exceptions import AuthenticationRequiredForGenerationError

# Create a blueprint with standardized prefix
lemma_api_bp = Blueprint("lemma_api", __name__, url_prefix="/api/lang/lemma")

logger = logging.getLogger(__name__)


@lemma_api_bp.route("/<target_language_code>/<lemma>/data")
def get_lemma_data_api(target_language_code: str, lemma: str):
    """Get detailed data for a specific lemma."""
    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
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
    # Still using target_language_code as parameter for backward compatibility
    lemmas = Lemma.get_all_lemmas_for(
        target_language_code=target_language_code, sort_by=sort
    )

    # Transform the response to match the frontend's expected format
    lemma_list = []
    for lemma_obj in lemmas:
        lemma_data = lemma_obj.to_dict()
        # Add any additional fields the frontend might need
        lemma_list.append(lemma_data)

    return jsonify(lemma_list)


@lemma_api_bp.route("/<target_language_code>/lemma/<lemma>/metadata")
@api_auth_optional
def get_lemma_metadata_api(target_language_code: str, lemma: str):
    """Get detailed metadata for a lemma.

    This API endpoint corresponds to the get_lemma_metadata_vw view function.
    It returns complete metadata for a lemma, including default values for missing fields.

    If the lemma doesn't exist, it will be generated using Claude AI.
    """
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)

    try:
        # This will now potentially raise AuthenticationRequiredForGenerationError
        lemma_data = load_or_generate_lemma_metadata(
            lemma=lemma,
            target_language_code=target_language_code,
            generate_if_incomplete=True,
        )

        # Find the lemma model - it should exist now
        lemma_model = Lemma.get(
            Lemma.lemma == lemma,
            Lemma.target_language_code == target_language_code,
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

    except AuthenticationRequiredForGenerationError:
        # Handle the case where generation requires login
        error_data = {
            "error": "Authentication Required",
            "description": "Authentication required to generate full lemma details",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "authentication_required_for_generation": True,  # Add a flag for frontend
        }
        # Attempt to return partial data if lemma exists but is incomplete
        try:
            lemma_model = Lemma.get(
                Lemma.lemma == lemma,
                Lemma.target_language_code == target_language_code,
            )
            error_data["partial_lemma_metadata"] = lemma_model.to_dict()
            error_data["metadata"] = {
                "created_at": lemma_model.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": lemma_model.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        except DoesNotExist:
            # If lemma doesn't exist at all, just return the 401 error
            pass
        return jsonify(error_data), 401

    except DoesNotExist:
        # This case should theoretically not be hit anymore as load_or_generate
        # handles creation, but kept for safety.
        error_data = {
            "error": "Not Found",
            "description": f"Lemma '{lemma}' not found and could not be generated.",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
        }
        response = jsonify(error_data)
        response.status_code = 404
        return response

    except Exception as e:
        # Handle other potential errors during generation/loading
        logger.exception(
            f"Error in get_lemma_metadata_api for lemma '{lemma}': {str(e)}"
        )
        error_data = {
            "error": "Failed to process lemma",
            "description": f"Could not retrieve or generate metadata for lemma '{lemma}': {str(e)}",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
        }
        response = jsonify(error_data)
        response.status_code = 500
        return response


@lemma_api_bp.route(
    "/<target_language_code>/<lemma>/complete_metadata", methods=["POST"]
)
@api_auth_required
def complete_lemma_metadata_api(target_language_code: str, lemma: str):
    """Complete the metadata for a specific lemma.

    This API endpoint processes an individual lemma to generate full metadata.
    It is designed to be called as part of the frontend-orchestrated processing queue.
    """
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)

    try:
        # Get the lemma model
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )

        # Complete the metadata
        lemma_model = complete_lemma_metadata(lemma_model)

        # Return the completed lemma data
        return jsonify(
            {
                "success": True,
                "lemma": lemma_model.to_dict(),
            }
        )

    except DoesNotExist:
        response = jsonify(
            {"error": "Not Found", "description": f"Lemma '{lemma}' not found"}
        )
        response.status_code = 404
        return response

    except Exception as e:
        response = jsonify(
            {"error": "Failed to complete lemma metadata", "description": str(e)}
        )
        response.status_code = 500
        return response
