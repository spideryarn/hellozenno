"""Main Flask application."""

import os
import sys

# Add the parent directory to sys.path to allow importing from the root directory
# This must be done before any imports from modules within the project
my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(my_path)
print(my_path)
# sys.exit(0)

import traceback
from loguru import logger
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from whitenoise import WhiteNoise

# We no longer need the Vite helpers import since we're using SvelteKit for frontend
from utils.env_config import is_vercel, FLASK_SECRET_KEY
from utils.logging_utils import setup_logging
from utils.url_utils import decode_url_params
from utils.url_registry import generate_route_registry, generate_typescript_routes

# Configure logging with loguru
setup_logging(log_to_file=True, max_lines=200)


def create_app():
    """Create and configure the Flask application."""
    logger.info("Creating Flask application")

    # Simplified app initialization - we only need static_folder now
    app = Flask(
        __name__,
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../static"
        ),
    )

    # Enable CORS for API endpoints
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {"origins": "*"},  # Allow all origins for API endpoints
            # r"/lang/*/flashcards/*": {
            #     "origins": "*"
            # },  # Allow all origins for flashcard endpoints with new URL structure
            # r"/api/lang/*": {
            #     "origins": "*"
            # },  # Allow all origins for language-related API endpoints
        },
    )

    app.config["SECRET_KEY"] = FLASK_SECRET_KEY

    # Set production flag based on environment
    app.config["IS_PRODUCTION"] = is_vercel()

    # Check if we're in local check of production frontend mode
    # Use the new, more explicit environment variable name
    if os.environ.get("LOCAL_CHECK_OF_PROD_FRONTEND") == "true":
        app.config["LOCAL_CHECK_OF_PROD_FRONTEND"] = True
        logger.info("Running in LOCAL_CHECK_OF_PROD_FRONTEND mode")

    # We no longer need to register Vite helpers as we're using SvelteKit

    # Initialize database
    from utils.db_connection import init_db

    init_db(app)

    # Register blueprints
    from views.system_views import system_views_bp

    # from views.auth_views import auth_views_bp # Comment out this import
    from views.auth_api import auth_api_bp
    from views.core_views import core_views_bp
    from views.wordform_views import wordform_views_bp
    from views.lemma_views import lemma_views_bp
    from views.sourcedir_views import sourcedir_views_bp
    from views.sourcefile_views import sourcefile_views_bp
    from views.phrase_views import phrase_views_bp
    from views.sentence_views import sentence_views_bp
    from views.search_views import search_views_bp
    from views.flashcard_views import flashcard_views_bp
    from views.languages_views import languages_views_bp

    # Register system views first to ensure essential routes are matched first
    app.register_blueprint(system_views_bp)

    # Register system management blueprints
    # app.register_blueprint(auth_views_bp) # Comment out this registration
    app.register_blueprint(auth_api_bp)

    # Register remaining blueprints
    app.register_blueprint(core_views_bp)
    app.register_blueprint(languages_views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(search_views_bp)
    app.register_blueprint(flashcard_views_bp)

    # Register the new API blueprints
    from views.sourcedir_api import sourcedir_api_bp
    from views.wordform_api import wordform_api_bp
    from views.lemma_api import lemma_api_bp
    from views.phrase_api import phrase_api_bp
    from views.sourcefile_api import sourcefile_api_bp
    from views.sourcefile_api_processing import sourcefile_processing_api_bp
    from views.sentence_api import sentence_api_bp
    from views.languages_api import languages_api_bp
    from views.flashcard_api import flashcard_api_bp
    from views.search_api import search_api_bp
    from views.profile_api import profile_api_bp

    app.register_blueprint(sourcedir_api_bp)
    app.register_blueprint(wordform_api_bp)
    app.register_blueprint(lemma_api_bp)
    app.register_blueprint(phrase_api_bp)
    app.register_blueprint(sourcefile_api_bp)
    app.register_blueprint(sourcefile_processing_api_bp)
    app.register_blueprint(sentence_api_bp)
    app.register_blueprint(languages_api_bp)
    app.register_blueprint(flashcard_api_bp)
    app.register_blueprint(search_api_bp)
    app.register_blueprint(profile_api_bp)

    # Add middleware to handle URL decoding for all routes - see planning/250316_vercel_url_encoding_fix.md
    app.before_request(decode_url_params)

    # Configure WhiteNoise for static file serving - still needed for audio, downloads, etc.
    static_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../static"
    )

    # Wrap the WSGI app with WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app)

    # Add static files with appropriate prefixes
    app.wsgi_app.add_files(static_folder, prefix="static/")

    # Enable compression and caching for better performance
    app.wsgi_app.enable_compression = True  # type: ignore
    app.wsgi_app.caching = True  # type: ignore

    # Log WhiteNoise configuration
    logger.info(f"WhiteNoise configured with static folder: {static_folder}")
    logger.info(f"WhiteNoise compression enabled: {app.wsgi_app.enable_compression}")  # type: ignore

    # Generate route registry and TypeScript definitions
    with app.app_context():
        # Generate route registry
        route_registry = generate_route_registry(app)

        # Make route registry available to templates
        @app.context_processor
        def inject_routes():
            return {
                "route_registry": route_registry,
            }

        # In development mode, generate TypeScript routes file
        if not app.config["IS_PRODUCTION"]:
            ts_output_path = generate_typescript_routes(app)
            logger.info(f"Generated TypeScript routes at {ts_output_path}")

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        # Check if this is an API request
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "error": "Not found",
                        "status_code": 404,
                        "endpoint": request.endpoint,
                        "url": request.url,
                    }
                ),
                404,
            )
        return render_template("404.jinja"), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors with detailed logging and appropriate response format.
        Focus on providing detailed error information for API routes."""
        # Get the original exception
        original_error = getattr(e, "original_exception", e)

        # Log the full error with traceback
        logger.exception(f"Unhandled exception: {str(original_error)}")

        # For API requests, always return a JSON response with useful details
        if request.path.startswith("/api/"):
            response = {
                "error": "Internal server error",
                "status_code": 500,
                "message": str(original_error),
            }

            # In development, include more details
            if not app.config["IS_PRODUCTION"]:
                response["exception_type"] = type(original_error).__name__
                response["traceback"] = traceback.format_exc()
                response["endpoint"] = request.endpoint
                response["url"] = request.url
                response["method"] = request.method

            return jsonify(response), 500

        # For web requests, return the error template or a basic error
        return "Internal Server Error", 500

    # Added CLI command to generate routes
    @app.cli.command("generate-routes-ts")
    def generate_routes_ts_command():
        """Generate TypeScript route definitions from Flask app.url_map."""
        with app.app_context():
            ts_output_path = generate_typescript_routes(app)
        logger.info(f"Generated TypeScript routes at {ts_output_path}")

    logger.info("Application initialized successfully")
    return app


# Create the Flask application instance
app = create_app()


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
