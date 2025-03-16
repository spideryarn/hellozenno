"""Main Flask application."""

import os
import sys
import json
from loguru import logger
from flask import Flask, Request, jsonify
from flask_cors import CORS

# Add the parent directory to sys.path to allow importing from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.env_config import is_vercel, FLASK_SECRET_KEY
from utils.logging_utils import setup_logging

# Configure logging with loguru
setup_logging(log_to_file=True, max_lines=100)


# Debug: Print all environment variables
def debug_env_vars():
    env_vars = {k: v for k, v in os.environ.items()}
    return json.dumps(env_vars, indent=2)


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


@app.route("/")
def home():
    return "Hello from Vercel Flask app!"


@app.route("/vercel-test")
def vercel_test():
    return "Hello from Vercel serverless function!"


@app.route("/debug-env")
def debug_env():
    return debug_env_vars()


# Vercel serverless handler
def handler(request):
    """Handle requests in Vercel serverless environment."""
    return app(request.environ, start_response)


def start_response(status, headers, exc_info=None):
    """WSGI start_response function."""
    return [status, headers]


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
