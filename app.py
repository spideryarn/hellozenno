"""Main Flask application."""

import logging
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from utils.env_config import is_fly_cloud, FLASK_SECRET_KEY

# from flask_pw import Peewee as FLPeewee

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    logger.info("Creating Flask application")

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

    app.config["SECRET_KEY"] = FLASK_SECRET_KEY

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
    from utils.db_connection import init_db

    init_db(app)

    # Register blueprints
    from views.views import views_bp
    from views.wordform_views import wordform_views_bp
    from views.lemma_views import lemma_views_bp
    from views.sourcedir_views import sourcedir_views_bp
    from views.sourcefile_views import sourcefile_views_bp
    from views.phrase_views import phrase_views_bp
    from views.sentence_views import sentence_views_bp
    from views.api import api_bp
    from views.flashcard_views import flashcard_views_bp
    from views.system_views import system_views_bp

    # Register system views first to ensure health check route is matched before language routes
    app.register_blueprint(system_views_bp)

    # Register remaining blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(flashcard_views_bp)

    logger.info("Application initialized successfully")
    return app


app = create_app()
