"""API endpoints for lemmas.

All endpoints for interacting with lemmas programmatically.
These endpoints follow the standard pattern:
/api/lang/lemma/...
"""

from flask import Blueprint, jsonify, request, send_file
import io
from peewee import DoesNotExist
import logging
import urllib.parse

from utils.lang_utils import get_language_name
from db_models import Lemma, UserLemma, LemmaAudio
from utils.store_utils import load_or_generate_lemma_metadata
from utils.sourcefile_utils import complete_lemma_metadata
from utils.audio_utils import ensure_audio_data

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


# -------------------------
# Lemma audio endpoints
# -------------------------


@lemma_api_bp.route("/<target_language_code>/<lemma>/audio/variants", methods=["GET"])
def get_lemma_audio_variants_api(target_language_code: str, lemma: str):
    """List available audio variants for a lemma by provider/voice.

    Public endpoint: returns empty list if none exist.
    """
    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )
    except DoesNotExist:
        return jsonify({"error": "Lemma not found"}), 404

    variants = (
        LemmaAudio.select()
        .where(LemmaAudio.lemma == lemma_model)
        .order_by(LemmaAudio.created_at)
    )
    out = []
    for v in variants:
        out.append(
            {
                "provider": v.provider,
                "voice_name": v.voice_name,
                "url": f"/api/lang/lemma/{target_language_code}/{lemma}/audio/{v.provider}/{v.voice_name}",
            }
        )
    return jsonify(out)


@lemma_api_bp.route(
    "/<target_language_code>/<lemma>/audio/<provider>/<voice_name>", methods=["GET"]
)
def get_lemma_audio_stream_api(
    target_language_code: str, lemma: str, provider: str, voice_name: str
):
    """Stream a specific lemma audio variant by provider/voice.

    Public endpoint; 404 if not found.
    """
    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )
    except DoesNotExist:
        return jsonify({"error": "Lemma not found"}), 404

    try:
        row = LemmaAudio.get(
            (LemmaAudio.lemma == lemma_model)
            & (LemmaAudio.provider == provider)
            & (LemmaAudio.voice_name == voice_name)
        )
    except DoesNotExist:
        return jsonify({"error": "Audio not found"}), 404

    return send_file(
        io.BytesIO(row.audio_data), mimetype="audio/mpeg", as_attachment=False
    )


@lemma_api_bp.route("/<target_language_code>/<lemma>/audio/ensure", methods=["POST"])
@api_auth_required
def ensure_lemma_audio_api(target_language_code: str, lemma: str):
    """Ensure N distinct audio variants exist for a lemma.

    Query param: n (default 3). Uses global ELEVENLABS voice pool; disables delays.
    """
    try:
        from config import LEMMA_AUDIO_SAMPLES

        n = int(request.args.get("n", str(LEMMA_AUDIO_SAMPLES)))
    except Exception:
        from config import LEMMA_AUDIO_SAMPLES

        n = LEMMA_AUDIO_SAMPLES

    try:
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )
    except DoesNotExist:
        return jsonify({"error": "Lemma not found"}), 404

    # Build existing set
    existing = set(
        (la.provider, la.voice_name)
        for la in LemmaAudio.select().where(LemmaAudio.lemma == lemma_model)
    )

    from config import ELEVENLABS_VOICE_POOL

    # Select missing voices until we reach n
    to_create = []
    for v in ELEVENLABS_VOICE_POOL:
        if ("elevenlabs", v) not in existing:
            to_create.append(("elevenlabs", v))
        if len(existing) + len(to_create) >= n:
            break

    # Generate and store
    for provider, voice_name in to_create:
        audio_bytes = ensure_audio_data(
            text=lemma_model.lemma,
            should_add_delays=False,
            should_play=False,
            verbose=0,
            voice_name=voice_name,
            voice_settings={
                "stability": 0.92,
            },
        )
        LemmaAudio.create(
            lemma=lemma_model,
            provider=provider,
            voice_name=voice_name,
            audio_data=audio_bytes,
        )

    return "", 204


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


@lemma_api_bp.route("/<target_language_code>/<lemma>/ignore", methods=["POST"])
@api_auth_required
def ignore_lemma_api(target_language_code: str, lemma: str):
    """Mark a lemma as ignored for the current user.

    This endpoint requires authentication and will add the lemma
    to the user's list of ignored lemmas.
    """
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)

    try:
        # Get the lemma model
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )

        # Get the user ID from Flask g object where api_auth_required stores it
        from flask import g

        user_id = g.user_id

        # Use the class method we defined in UserLemma
        user_lemma = UserLemma.ignore_lemma(user_id, lemma_model)

        return jsonify(
            {
                "success": True,
                "message": f"Lemma '{lemma}' ignored successfully",
                "ignored_dt": (
                    user_lemma.ignored_dt.isoformat() if user_lemma.ignored_dt else None  # type: ignore
                ),
            }
        )

    except DoesNotExist:
        response = jsonify(
            {"error": "Not Found", "description": f"Lemma '{lemma}' not found"}
        )
        response.status_code = 404
        return response

    except Exception as e:
        logger.exception(f"Error ignoring lemma '{lemma}': {str(e)}")
        response = jsonify({"error": "Failed to ignore lemma", "description": str(e)})
        response.status_code = 500
        return response


@lemma_api_bp.route("/<target_language_code>/<lemma>/unignore", methods=["POST"])
@api_auth_required
def unignore_lemma_api(target_language_code: str, lemma: str):
    """Remove a lemma from the user's ignored list.

    This endpoint requires authentication and will remove the lemma
    from the user's list of ignored lemmas.
    """
    # URL decode the lemma parameter to handle non-Latin characters properly
    lemma = urllib.parse.unquote(lemma)

    try:
        # Get the lemma model
        lemma_model = Lemma.get(
            (Lemma.lemma == lemma)
            & (Lemma.target_language_code == target_language_code)
        )

        # Get the user ID from Flask g object where api_auth_required stores it
        from flask import g

        user_id = g.user_id

        # Use the class method we defined in UserLemma
        success = UserLemma.unignore_lemma(user_id, lemma_model)

        if success:
            return jsonify(
                {"success": True, "message": f"Lemma '{lemma}' unignored successfully"}
            )
        else:
            return jsonify(
                {"success": True, "message": f"Lemma '{lemma}' was not ignored"}
            )

    except DoesNotExist:
        response = jsonify(
            {"error": "Not Found", "description": f"Lemma '{lemma}' not found"}
        )
        response.status_code = 404
        return response

    except Exception as e:
        logger.exception(f"Error unignoring lemma '{lemma}': {str(e)}")
        response = jsonify({"error": "Failed to unignore lemma", "description": str(e)})
        response.status_code = 500
        return response


@lemma_api_bp.route("/<target_language_code>/ignored")
@api_auth_required
def get_ignored_lemmas_api(target_language_code: str):
    """Get all lemmas that the current user has ignored.

    This endpoint requires authentication and returns the list of
    lemmas that the user has marked as ignored.
    """
    try:
        # Get the user ID from Flask g object where api_auth_required stores it
        from flask import g

        user_id = g.user_id

        # Get all ignored lemmas for this user and language
        ignored_lemmas = (
            UserLemma.select(UserLemma, Lemma)
            .join(Lemma)
            .where(
                (UserLemma.user_id == user_id)
                & (UserLemma.ignored_dt.is_null(False))
                & (Lemma.target_language_code == target_language_code)
            )
            .order_by(UserLemma.ignored_dt.desc())
        )

        # Build response
        result = []
        for ul in ignored_lemmas:
            result.append(
                {
                    "lemma": ul.lemma.lemma,
                    "target_language_code": ul.lemma.target_language_code,
                    "ignored_dt": ul.ignored_dt.isoformat() if ul.ignored_dt else None,
                    "translations": ul.lemma.translations,
                }
            )

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error getting ignored lemmas: {str(e)}")
        response = jsonify(
            {"error": "Failed to get ignored lemmas", "description": str(e)}
        )
        response.status_code = 500
        return response


@lemma_api_bp.route("/<target_language_code>/lemma/<lemma>/delete", methods=["POST"])
@api_auth_required
def delete_lemma_api(target_language_code: str, lemma: str):
    """Delete a lemma and its associated wordforms via cascade delete."""
    # URL decode the lemma parameter to handle non-Latin characters properly
    # Defense in depth: decode explicitly here, in addition to middleware
    lemma = urllib.parse.unquote(lemma)

    try:
        lemma_model = Lemma.get(
            Lemma.lemma == lemma,
            Lemma.target_language_code == target_language_code,
        )
        # Simply delete the lemma - wordforms will be deleted by cascade
        lemma_model.delete_instance()
        # Return 204 No Content on successful deletion
        return "", 204
    except DoesNotExist:
        # Also return 204 if it doesn't exist, as the resource is effectively gone
        return "", 204
