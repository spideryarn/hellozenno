from flask import Blueprint, render_template
from utils.lang_utils import get_all_languages

# Create a language-specific blueprint
languages_views_bp = Blueprint("languages_views", __name__)

# Configure logging
import logging

logger = logging.getLogger(__name__)


@languages_views_bp.route("/language", strict_slashes=False)
def languages_list_vw():
    """Display all supported languages."""
    languages = get_all_languages()
    return render_template(
        "languages.jinja",
        languages=languages,
    )
