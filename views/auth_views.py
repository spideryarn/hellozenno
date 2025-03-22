from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    g,
    flash,
)
from peewee import DoesNotExist

from utils.auth_utils import (
    page_auth_required,
    get_current_user,
)
from db_models import Profile
from config import SUPPORTED_LANGUAGES

# Create auth-specific blueprint
auth_views_bp = Blueprint("auth_views", __name__, url_prefix="/auth")

# Configure logging
import logging
logger = logging.getLogger(__name__)


@auth_views_bp.route("/", methods=["GET"])
@auth_views_bp.route("/<target_language_code>", methods=["GET"])
def auth_page_vw(target_language_code=None):
    """Render the auth page with login and signup forms."""
    # Catch empty string language code (from trailing slash) and redirect to /auth
    if target_language_code == "":
        return redirect("/auth/")

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


@auth_views_bp.route("/protected")
@page_auth_required
def protected_page_vw():
    """A protected page that requires authentication."""
    # Get user profile
    try:
        profile = Profile.get(Profile.user_id == g.user["id"])
    except DoesNotExist:
        profile = None

    return render_template("protected.jinja", user=g.user, profile=profile)


@auth_views_bp.route("/profile", methods=["GET", "POST"])
@auth_views_bp.route("/profile/<target_language_code>", methods=["GET", "POST"])
@page_auth_required
def profile_page_vw(target_language_code=None):
    """User profile page for editing preferences."""
    # Catch empty string language code (from trailing slash) and redirect to /auth/profile
    if target_language_code == "":
        return redirect("/auth/profile")

    # Get or create profile
    profile, created = Profile.get_or_create_for_user(g.user["id"], g.user["email"])

    if request.method == "POST":
        # Update profile with form data
        profile.target_language_code = request.form.get("target_language_code") or None
        profile.save()

        flash("Profile updated successfully!")
        return redirect(url_for("auth_views.profile_page_vw"))

    # GET request - show the profile form
    # Explicitly set target_language_code to None to avoid language lookup errors in templates
    return render_template(
        "profile.jinja",
        user=g.user,
        profile=profile,
        languages=SUPPORTED_LANGUAGES,
        target_language_code=None,  # Pass None to avoid template errors
        target_language_name=None,  # Explicitly pass None for target_language_name
    )