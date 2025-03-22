from flask import (
    Blueprint,
    jsonify,
    request,
    g,
)

from utils.auth_utils import (
    api_auth_required,
    set_auth_cookie,
    clear_auth_cookie,
)

# Create auth-specific API blueprint
auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")

# Configure logging
import logging
logger = logging.getLogger(__name__)


@auth_api_bp.route("/session", methods=["POST", "DELETE"])
def manage_session_api():
    """
    Handle session management for auth.

    POST: Set a session cookie with the JWT token
    DELETE: Clear the session cookie
    """
    if request.method == "POST":
        # Set the auth cookie with the token from the request
        data = request.get_json()
        if not data or "token" not in data:
            return jsonify({"error": "Token is required"}), 400

        # Create a response with the cookie
        response = set_auth_cookie(data["token"])
        return response, 200

    elif request.method == "DELETE":
        # Clear the auth cookie
        response = clear_auth_cookie()
        return response, 200

    # Should never reach here
    return jsonify({"error": "Method not allowed"}), 405


@auth_api_bp.route("/user", methods=["GET"])
@api_auth_required
def get_user_api():
    """Get the current authenticated user's info."""
    # g.user is set by the api_auth_required decorator
    return jsonify(g.user), 200