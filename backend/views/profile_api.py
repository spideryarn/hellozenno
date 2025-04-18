from flask import Blueprint, jsonify, request, g
from peewee import DoesNotExist
from loguru import logger

from utils.auth_utils import api_auth_required
from db_models import Profile
from utils.lang_utils import VALID_target_language_codeS, get_language_name

profile_api_bp = Blueprint("profile_api", __name__, url_prefix="/api/profile")


@profile_api_bp.route("/", methods=["GET"])
@api_auth_required
def get_profile_api():
    """Get the current authenticated user's profile."""
    try:
        # g.user is set by api_auth_required
        profile, created = Profile.get_or_create_for_user(g.user["id"], g.user["email"])
        if created:
            logger.info(f"Created profile for user {g.user['id']} ({g.user['email']})")
        return jsonify(profile.to_dict()), 200
    except Exception as e:
        logger.exception(f"Error fetching profile for user {g.user.get('id')}: {e}")
        return jsonify({"error": "Failed to fetch profile"}), 500


@profile_api_bp.route("/", methods=["PUT"])
@api_auth_required
def update_profile_api():
    """Update the current authenticated user's profile."""
    try:
        profile, _ = Profile.get_or_create_for_user(g.user["id"], g.user["email"])
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # --- Update target_language_code ---
        if "target_language_code" in data:
            new_lang_code = data["target_language_code"]

            # Handle empty string or null to clear the preference
            if new_lang_code is None or new_lang_code == "":
                profile.target_language_code = None
                logger.info(f"Cleared target language for user {g.user['id']}")
            # Validate the new language code
            elif new_lang_code not in VALID_target_language_codeS:
                logger.warning(
                    f"Invalid target language code '{new_lang_code}' provided by user {g.user['id']}"
                )
                return (
                    jsonify({"error": f"Invalid language code: {new_lang_code}"}),
                    400,
                )
            else:
                # Update only if different to avoid unnecessary writes
                if profile.target_language_code != new_lang_code:
                    profile.target_language_code = new_lang_code
                    logger.info(
                        f"Updated target language for user {g.user['id']} to {new_lang_code}"
                    )

        # --- Add other fields here if needed ---

        profile.save()
        return jsonify(profile.to_dict()), 200

    except Exception as e:
        logger.exception(f"Error updating profile for user {g.user.get('id')}: {e}")
        return jsonify({"error": "Failed to update profile"}), 500
