"""Main Flask application."""

import logging
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from fly_cloud_utils import is_fly_cloud

# from flask_pw import Peewee as FLPeewee

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate the environment configuration."""
    logger.info("Validating environment...")

    # Check if we're running in Cloud Run
    if is_fly_cloud():
        from _secrets import (
            POSTGRES_DB_PASSWORD,
            POSTGRES_DB_USER,
            POSTGRES_DB_NAME,
        )
    logger.info("Environment validation successful")


def create_app():
    """Create and configure the Flask application."""
    logger.info("Creating Flask application")

    # Validate environment before creating app
    validate_environment()

    app = Flask(__name__)

    # Enable CORS for API and flashcard endpoints
    CORS(
        app,
        resources={
            r"/api/*": {"origins": "*"},  # Allow all origins for API endpoints
            r"/*/flashcards/*": {
                "origins": "*"
            },  # Allow all origins for flashcard endpoints
        },
    )

    # Load configuration
    from config import SECRET_KEY

    app.config["SECRET_KEY"] = SECRET_KEY

    # Only enable Debug Toolbar in development
    if not is_fly_cloud():
        try:
            from flask_debugtoolbar import DebugToolbarExtension

            app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
            toolbar = DebugToolbarExtension(app)
            logger.info("Debug Toolbar initialized")
        except ImportError:
            logger.info("Debug Toolbar not available")

    # Initialize database
    from db_connection import init_db

    init_db(app)

    # Register blueprints
    from views import views_bp
    from wordform_views import wordform_views_bp
    from lemma_views import lemma_views_bp
    from sourcedir_views import sourcedir_views_bp
    from sourcefile_views import sourcefile_views_bp
    from phrase_views import phrase_views_bp
    from sentence_views import sentence_views_bp
    from api import api_bp
    from flashcard_views import flashcard_views_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(flashcard_views_bp)

    # Add favicon route - handle both with and without trailing slash
    @app.route("/favicon.ico", defaults={"trailing_slash": ""})
    @app.route("/favicon.ico/", defaults={"trailing_slash": "/"})
    def favicon(trailing_slash):
        return send_from_directory(
            os.path.join(app.root_path, "static", "img"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    logger.info("Application initialized successfully")
    return app


app = create_app()
