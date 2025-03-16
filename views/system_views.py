from datetime import datetime
import logging
import json
from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    g,
    flash,
)
from peewee import DoesNotExist

from utils.db_connection import get_db
from utils.env_config import is_vercel
from utils.auth_utils import (
    page_auth_required,
    api_auth_required,
    get_current_user,
    set_auth_cookie,
    clear_auth_cookie,
)
from db_models import Profile
from config import SUPPORTED_LANGUAGES

# Create blueprint for system views
system_views_bp = Blueprint("system_views", __name__, url_prefix="")

# Configure logging
logger = logging.getLogger(__name__)


@system_views_bp.route("/health-check")
def health_check():
    """Health check endpoint that verifies app and database functionality."""
    try:
        # Get database metrics
        db = get_db()
        db_metrics = get_db_metrics(db)

        # Get application metrics
        app_metrics = {
            "timestamp": datetime.now().isoformat(),
        }

        # Determine overall status based on database connectivity
        is_healthy = db_metrics["connected"]

        response = {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_metrics,
            "application": app_metrics,
        }

        # Log metrics for monitoring
        logger.info("Health check metrics: %s", response)

        return jsonify(response), 200 if is_healthy else 500

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


def get_db_metrics(db):
    """Get database metrics.

    Args:
        db: Database connection

    Returns:
        dict: Database metrics
    """
    try:
        # Test database connection with a simple query
        cursor = db.execute_sql("SELECT 1")
        cursor.fetchone()
        cursor.close()

        # Get connection info
        connection_info = {
            "database": db.database,
            "host": db.connect_params.get("host", "unknown"),
            "port": db.connect_params.get("port", "unknown"),
        }

        return {
            "connected": True,
            "connection_info": connection_info,
        }
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return {
            "connected": False,
            "error": str(e),
        }


@system_views_bp.route("/auth", methods=["GET"])
@system_views_bp.route("/auth/<target_language_code>", methods=["GET"])
def auth_page(target_language_code=None):
    """Render the auth page with login and signup forms."""
    # Catch empty string language code (from trailing slash) and redirect to /auth
    if target_language_code == "":
        return redirect("/auth")
        
    # Check if a redirect URL was provided
    redirect_url = request.args.get("redirect", "/")
    show_signup = request.args.get("signup", "false").lower() == "true"

    # If the user is already authenticated, redirect to the home page
    user = get_current_user()
    if user:
        return redirect(redirect_url)

    return render_template(
        "auth.jinja",
        redirect_url=redirect_url,
        show_signup=show_signup,
        target_language_code=target_language_code,
    )


@system_views_bp.route("/api/auth/session", methods=["POST", "DELETE"])
def manage_session():
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


@system_views_bp.route("/api/auth/user", methods=["GET"])
@api_auth_required
def get_user():
    """Get the current authenticated user's info."""
    # g.user is set by the api_auth_required decorator
    return jsonify(g.user), 200


@system_views_bp.route("/protected")
@page_auth_required
def protected_page():
    """A protected page that requires authentication."""
    # Get user profile
    try:
        profile = Profile.get(Profile.user_id == g.user["id"])
    except DoesNotExist:
        profile = None

    return render_template("protected.jinja", user=g.user, profile=profile)


@system_views_bp.route("/profile", methods=["GET", "POST"])
@system_views_bp.route("/profile/<target_language_code>", methods=["GET", "POST"])
@page_auth_required
def profile_page(target_language_code=None):
    """User profile page for editing preferences."""
    # Catch empty string language code (from trailing slash) and redirect to /profile
    if target_language_code == "":
        return redirect("/profile")
        
    # Get or create profile
    profile, created = Profile.get_or_create_for_user(g.user["id"], g.user["email"])

    if request.method == "POST":
        # Update profile with form data
        profile.target_language_code = request.form.get("target_language_code") or None
        profile.save()

        flash("Profile updated successfully!")
        return redirect(url_for("system_views.profile_page"))

    # GET request - show the profile form
    # Explicitly set target_language_code to None to avoid language lookup errors in templates
    return render_template(
        "profile.jinja", 
        user=g.user, 
        profile=profile, 
        languages=SUPPORTED_LANGUAGES,
        target_language_code=None,  # Pass None to avoid template errors
        target_language_name=None  # Explicitly pass None for target_language_name
    )
