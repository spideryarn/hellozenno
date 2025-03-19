"""Core API endpoints.

Contains the base API routes and documentation.
"""

from flask import Blueprint, jsonify, redirect, url_for
from utils.flask_view_utils import full_url_for

# Create the core API blueprint
core_api_bp = Blueprint("core_api", __name__, url_prefix="/api")


@core_api_bp.route("/")
def home():
    """API home page."""
    return redirect(url_for("core_api.urls"))
