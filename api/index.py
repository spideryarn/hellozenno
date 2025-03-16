"""Main Flask application."""

import os
import sys
from loguru import logger
from flask import Flask
from flask_cors import CORS
from whitenoise import WhiteNoise

# Add the parent directory to sys.path to allow importing from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.env_config import is_vercel, FLASK_SECRET_KEY
from utils.logging_utils import setup_logging
from utils.url_utils import decode_url_params


# Configure logging with loguru
setup_logging(log_to_file=True, max_lines=200)


def load_vite_manifest():
    """Load the Vite manifest file for asset versioning."""
    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "static/build/.vite/manifest.json",
    )
    try:
        import json

        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                return json.load(f)
        else:
            logger.warning(f"Vite manifest not found at {manifest_path}")
            return {}
    except Exception as e:
        logger.error(f"Error loading Vite manifest: {e}")
        return {}


def create_app():
    """Create and configure the Flask application."""
    logger.info("Creating Flask application")

    # Set template_folder to point to the templates directory at the root level
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"
        ),
    )

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

    # Load Vite manifest for asset versioning
    app.config["VITE_MANIFEST"] = load_vite_manifest()

    # Make manifest available to templates
    @app.context_processor
    def inject_vite_manifest():
        return {"vite_manifest": app.config["VITE_MANIFEST"]}

    # Initialize database
    from utils.db_connection import init_db

    init_db(app)

    # Register blueprints
    from views.system_views import system_views_bp
    from views.views import views_bp
    from views.wordform_views import wordform_views_bp
    from views.lemma_views import lemma_views_bp
    from views.sourcedir_views import sourcedir_views_bp
    from views.sourcefile_views import sourcefile_views_bp
    from views.phrase_views import phrase_views_bp
    from views.sentence_views import sentence_views_bp
    from views.search_views import search_views_bp
    from views.api import api_bp
    from views.flashcard_views import flashcard_views_bp

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
    app.register_blueprint(search_views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(flashcard_views_bp)

    # Add middleware to handle URL decoding for all routes - see planning/250316_vercel_url_encoding_fix.md
    app.before_request(decode_url_params)

    # Configure WhiteNoise for static file serving
    static_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"
    )
    templates_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
    )

    # Wrap the WSGI app with WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app)

    # Add static files with appropriate prefixes
    app.wsgi_app.add_files(static_folder, prefix="static/")

    # Enable compression and caching for better performance
    app.wsgi_app.enable_compression = True
    app.wsgi_app.caching = True

    # Log WhiteNoise configuration
    logger.info(f"WhiteNoise configured with static folder: {static_folder}")
    logger.info(f"WhiteNoise compression enabled: {app.wsgi_app.enable_compression}")

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
