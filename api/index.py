"""Main Flask application."""

import os
import sys

# Add the parent directory to sys.path to allow importing from the root directory
# This must be done before any imports from modules within the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from flask import Flask, render_template
from flask_cors import CORS
from whitenoise import WhiteNoise

# Import the consolidated Vite helpers from utils/vite_helpers.py
from utils.vite_helpers import (
    register_vite_helpers,
    get_vite_manifest,
    vite_asset_url,
    dump_manifest,
)
from utils.env_config import is_vercel, FLASK_SECRET_KEY
from utils.logging_utils import setup_logging
from utils.url_utils import decode_url_params
from utils.url_registry import generate_route_registry, generate_typescript_routes


def setup_route_registry(app, static_folder):
    """Set up route registry and generate TypeScript definitions.

    Args:
        app: The Flask application
        static_folder: Path to the static files directory
    """
    with app.app_context():
        # Generate route registry
        route_registry = generate_route_registry(app)

        # Make route registry available to templates
        @app.context_processor
        def inject_routes():
            # even though this is marked as unused by the IDE, it is actually being injected into the template context processor
            """Make route registry available to all templates."""
            return {
                "route_registry": route_registry,
            }

        # In development mode, generate TypeScript routes file
        if not app.config["IS_PRODUCTION"]:
            # Create directory for SvelteKit routes
            ts_output_path = "sveltekit_hz/src/lib/generated/routes.ts"
            os.makedirs(os.path.dirname(ts_output_path), exist_ok=True)

            # Generate TypeScript routes
            generate_typescript_routes(app, ts_output_path)
            logger.info(f"Generated TypeScript routes at {ts_output_path}")

    return route_registry


# Configure logging with loguru
setup_logging(log_to_file=True, max_lines=200)


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
            r"/lang/*/flashcards/*": {
                "origins": "*"
            },  # Allow all origins for flashcard endpoints with new URL structure
            r"/api/lang/*": {
                "origins": "*"
            },  # Allow all origins for language-related API endpoints
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

    # First import the functions directly
    from utils.vite_helpers import get_vite_manifest, vite_asset_url, dump_manifest

    # Register Vite helper functions directly as Jinja globals
    # This makes them available in all templates, including macros
    app.jinja_env.globals.update(
        vite_manifest=get_vite_manifest,
        vite_asset_url=vite_asset_url,
        dump_manifest=dump_manifest,
    )

    # Register the full vite helpers which adds a route for manifest viewing
    register_vite_helpers(app)

    # Initialize database
    from utils.db_connection import init_db

    init_db(app)

    # Register blueprints
    from views.system_views import system_views_bp
    from views.auth_views import auth_views_bp
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
    app.register_blueprint(auth_views_bp)
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
    from views.sentence_api import sentence_api_bp
    from views.languages_api import languages_api_bp
    from views.flashcard_api import flashcard_api_bp

    app.register_blueprint(sourcedir_api_bp)
    app.register_blueprint(wordform_api_bp)
    app.register_blueprint(lemma_api_bp)
    app.register_blueprint(phrase_api_bp)
    app.register_blueprint(sourcefile_api_bp)
    app.register_blueprint(sentence_api_bp)
    app.register_blueprint(languages_api_bp)
    app.register_blueprint(flashcard_api_bp)

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
    app.wsgi_app.enable_compression = True  # type: ignore
    app.wsgi_app.caching = True  # type: ignore

    # Log WhiteNoise configuration
    logger.info(f"WhiteNoise configured with static folder: {static_folder}")
    logger.info(f"WhiteNoise compression enabled: {app.wsgi_app.enable_compression}")  # type: ignore

    # Generate route registry and TypeScript definitions
    setup_route_registry(app, static_folder)

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.jinja"), 404

    # Test route to verify vite_helpers are properly registered
    @app.route("/dev/test-vite-helpers")
    def test_vite_helpers():
        from flask import current_app

        try:
            # Check context processors
            ctx = {}
            for processor in current_app.template_context_processors[None]:
                ctx.update(processor())

            # Check Jinja globals
            jinja_globals = {k: True for k in current_app.jinja_env.globals.keys()}

            # Return combined results
            return {
                "context_processor_functions": {
                    "vite_asset_url_available": "vite_asset_url" in ctx,
                    "vite_manifest_available": "vite_manifest" in ctx,
                    "dump_manifest_available": "dump_manifest" in ctx,
                    "available_context_functions": list(ctx.keys()),
                },
                "jinja_globals": {
                    "vite_asset_url_available": "vite_asset_url" in jinja_globals,
                    "vite_manifest_available": "vite_manifest" in jinja_globals,
                    "dump_manifest_available": "dump_manifest" in jinja_globals,
                    "available_global_functions": list(
                        k
                        for k in jinja_globals.keys()
                        if not k.startswith("_")
                        and callable(current_app.jinja_env.globals[k])
                    ),
                },
                "app_config": {
                    "IS_PRODUCTION": current_app.config.get("IS_PRODUCTION", False),
                    "LOCAL_CHECK_OF_PROD_FRONTEND": current_app.config.get(
                        "LOCAL_CHECK_OF_PROD_FRONTEND", False
                    ),
                },
            }
        except Exception as e:
            return {"error": str(e)}, 500

    # Added CLI command to generate routes
    @app.cli.command("generate-routes-ts")
    def generate_routes_ts_command():
        """Generate TypeScript route definitions from Flask app.url_map."""
        static_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"
        )
        output_path = os.path.join(static_folder, "js", "generated", "routes.ts")
        with app.app_context():
            generate_typescript_routes(app, output_path)
        logger.info(f"Generated TypeScript routes at {output_path}")

    logger.info("Application initialized successfully")
    return app


# Create the Flask application instance
app = create_app()


# This is important for Vercel deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
