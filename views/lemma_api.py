"""API endpoints for lemmas.

All endpoints for interacting with lemmas programmatically.
These endpoints follow the standard pattern:
/api/lang/lemma/...
"""

from flask import Blueprint, jsonify
from peewee import DoesNotExist
from db_models import Lemma

# Create a blueprint with standardized prefix
lemma_api_bp = Blueprint("lemma_api", __name__, url_prefix="/api/lang/lemma")


@lemma_api_bp.route("/<target_language_code>/<lemma>/data")
def get_lemma_data(target_language_code: str, lemma: str):
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