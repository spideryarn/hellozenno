from flask import (
    Blueprint,
    jsonify,
    request,
    g,
)

from utils.auth_utils import (
    api_auth_required,
)

# Create auth-specific API blueprint
auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")

# Configure logging
import logging

logger = logging.getLogger(__name__)


@auth_api_bp.route("/user", methods=["GET"])
@api_auth_required
def get_user_api():
    """Get the current authenticated user's info."""
    # g.user is set by the api_auth_required decorator
    return jsonify(g.user), 200
