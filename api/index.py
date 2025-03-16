"""Main Flask application."""

import os
import sys
from loguru import logger
from flask import Flask
from flask_cors import CORS

# Add the parent directory to sys.path to allow importing from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.env_config import is_vercel, FLASK_SECRET_KEY
from utils.logging_utils import setup_logging

# Configure logging with loguru
setup_logging(log_to_file=True, max_lines=100)


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

    # Set production flag based on environment
    app.config["IS_PRODUCTION"] = is_vercel()

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

    # Add a simple test route for Vercel deployment
    @app.route("/vercel-test")
    def vercel_test():
        return "Hello from Vercel serverless function!"

    logger.info("Application initialized successfully")
    return app


# Create the Flask application instance
app = create_app()


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
