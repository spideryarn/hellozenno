"""API endpoints for user profiles.

Endpoints for interacting with user profiles, preferences, and user-related data.
"""

from flask import Blueprint, jsonify, g, request
from peewee import DoesNotExist
from loguru import logger

from db_models import Profile, AuthUser
from utils.auth_utils import api_auth_required, get_user_by_id
from utils.lang_utils import VALID_target_language_codeS, get_language_name

# Create a blueprint with standardized prefix
profile_api_bp = Blueprint("profile_api", __name__, url_prefix="/api/profile")


@profile_api_bp.route("/current", methods=["GET"])
@api_auth_required
def get_current_profile_api():
    """Get the current user's profile information.
    
    Returns:
        JSON response with profile data
    """
    # g.profile is already set by the auth_required decorator
    if not g.profile:
        return jsonify({"error": "Profile not found"}), 404
    
    profile_data = g.profile.to_dict()
    
    # We no longer need to include email in the profile model itself
    # If we need email, get it from auth.users via g.user
    if g.user and "email" in g.user:
        profile_data["email"] = g.user.get("email")
    
    return jsonify({
        "success": True,
        "profile": profile_data
    })


@profile_api_bp.route("/update", methods=["PUT"])
@api_auth_required
def update_profile_api():
    """Update the current authenticated user's profile.
    
    Accepts:
        JSON body with profile fields to update, currently supporting:
        - target_language_code: The user's preferred language code
        
    Returns:
        JSON response with the updated profile data
    """
    try:
        # g.profile is already set by the auth_required decorator
        if not g.profile:
            return jsonify({"error": "Profile not found"}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # --- Update target_language_code ---
        if "target_language_code" in data:
            new_lang_code = data["target_language_code"]

            # Handle empty string or null to clear the preference
            if new_lang_code is None or new_lang_code == "":
                g.profile.target_language_code = None
                logger.info(f"Cleared target language for user {g.user['id']}")
            # Validate the new language code
            elif new_lang_code not in VALID_target_language_codeS:
                logger.warning(
                    f"Invalid target language code '{new_lang_code}' provided by user {g.user['id']}"
                )
                return (
                    jsonify({
                        "success": False,
                        "error": f"Invalid language code: {new_lang_code}"
                    }),
                    400,
                )
            else:
                # Update only if different to avoid unnecessary writes
                if g.profile.target_language_code != new_lang_code:
                    g.profile.target_language_code = new_lang_code
                    logger.info(
                        f"Updated target language for user {g.user['id']} to {new_lang_code}"
                    )

        # --- Add other profile fields here if needed ---

        g.profile.save()
        
        # Return the updated profile
        profile_data = g.profile.to_dict()
        if g.user and "email" in g.user:
            profile_data["email"] = g.user.get("email")
            
        return jsonify({
            "success": True,
            "profile": profile_data
        }), 200

    except Exception as e:
        logger.exception(f"Error updating profile for user {g.user.get('id')}: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to update profile: {str(e)}"
        }), 500


@profile_api_bp.route("/user/<user_id>", methods=["GET"])
@api_auth_required
def get_user_email_api(user_id):
    """Get a user's email by their ID.
    
    This endpoint is protected and requires authentication to prevent
    unauthorized access to user email addresses.
    
    Args:
        user_id: UUID of the user to look up
        
    Returns:
        JSON response with user_id and email
    """
    try:
        # Direct lookup from auth.users via AuthUser model
        try:
            auth_user = AuthUser.get_by_id(user_id)
            if not hasattr(auth_user, 'email'):
                # Be explicit about what's missing - fail fast
                return jsonify({
                    "success": False,
                    "error": "Email field not accessible in auth.users table"
                }), 500
                
            email = auth_user.email
            if not email:
                # Handle case where email exists but is null
                return jsonify({
                    "success": False, 
                    "error": "User has no email"
                }), 404
                
        except DoesNotExist:
            # Clear error when user doesn't exist
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
            
        # Return user information from helper method
        return jsonify({
            "success": True,
            "user_id": user_id,
            "email": email
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error retrieving user information: {str(e)}"
        }), 500