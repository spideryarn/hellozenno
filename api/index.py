"""Main Flask application."""

import os
import sys

# Add the parent directory to sys.path to allow importing from the root directory
# This must be done before any imports from modules within the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from flask import Flask
from flask_cors import CORS
from whitenoise import WhiteNoise

from utils.url_utils import load_vite_manifest

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
    from utils.url_registry import endpoint_for
    
    with app.app_context():
        # Generate route registry
        route_registry = generate_route_registry(app)
        
        # Make route registry available to templates
        @app.context_processor
        def inject_routes():
            """Make route registry available to all templates."""
            return {
                'route_registry': route_registry,
                'endpoint_for': endpoint_for  # Make endpoint_for available in all templates
            }
        
        # In development mode, generate TypeScript routes file
        if not app.config["IS_PRODUCTION"]:
            # Create a directory for generated files if it doesn't exist
            os.makedirs(os.path.join(static_folder, "js", "generated"), exist_ok=True)
            
            # Generate TypeScript routes
            ts_output_path = os.path.join(static_folder, "js", "generated", "routes.ts")
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

    # Load Vite manifest for asset versioning
    app.config["VITE_MANIFEST"] = load_vite_manifest()

    # Initialize database
    from utils.db_connection import init_db

    init_db(app)

    # Register blueprints
    from views.system_views import system_views_bp, auth_views_bp, sys_views_bp
    from views.views import views_bp
    from views.wordform_views import wordform_views_bp
    from views.lemma_views import lemma_views_bp
    from views.sourcedir_views import sourcedir_views_bp
    from views.sourcefile_views import sourcefile_views_bp
    from views.phrase_views import phrase_views_bp
    from views.sentence_views import sentence_views_bp
    from views.search_views import search_views_bp
    from views.flashcard_views import flashcard_views_bp

    # Register system views first to ensure essential routes are matched first
    app.register_blueprint(system_views_bp)

    # Register system management blueprints
    app.register_blueprint(sys_views_bp)
    app.register_blueprint(auth_views_bp)

    # Register remaining blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(search_views_bp)
    app.register_blueprint(flashcard_views_bp)

    # Register the new API blueprints
    from views.core_api import core_api_bp
    from views.sourcedir_api import sourcedir_api_bp
    from views.wordform_api import wordform_api_bp
    from views.lemma_api import lemma_api_bp
    from views.phrase_api import phrase_api_bp
    from views.sourcefile_api import sourcefile_api_bp
    from views.sentence_api import sentence_api_bp

    app.register_blueprint(core_api_bp)
    app.register_blueprint(sourcedir_api_bp)
    app.register_blueprint(wordform_api_bp)
    app.register_blueprint(lemma_api_bp)
    app.register_blueprint(phrase_api_bp)
    app.register_blueprint(sourcefile_api_bp)
    app.register_blueprint(sentence_api_bp)

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

    # Generate route registry and TypeScript definitions
    setup_route_registry(app, static_folder)
    
    # Add a context processor to provide blueprint and view function references to templates
    @app.context_processor
    def inject_view_functions():
        """Inject commonly used view functions and blueprints into all templates."""
        from views.views import views_bp, languages
        from views.wordform_views import wordform_views_bp, wordforms_list
        from views.lemma_views import lemma_views_bp, lemmas_list
        from views.phrase_views import phrase_views_bp, phrases_list
        from views.sentence_views import sentence_views_bp
        from views.search_views import search_views_bp, search_landing
        from views.flashcard_views import flashcard_views_bp
        from views.sourcedir_views import sourcedir_views_bp, sourcedirs_for_language, sourcefiles_for_sourcedir
        
        return {
            # Blueprints
            'views_bp': views_bp,
            'wordform_views_bp': wordform_views_bp,
            'lemma_views_bp': lemma_views_bp,
            'phrase_views_bp': phrase_views_bp,
            'sentence_views_bp': sentence_views_bp,
            'search_views_bp': search_views_bp,
            'flashcard_views_bp': flashcard_views_bp,
            'sourcedir_views_bp': sourcedir_views_bp,
            
            # Common view functions
            'languages': languages,
            'wordforms_list': wordforms_list,
            'lemmas_list': lemmas_list, 
            'phrases_list': phrases_list,
            'search_landing': search_landing,
            'sourcedirs_for_language': sourcedirs_for_language,
            'sourcefiles_for_sourcedir': sourcefiles_for_sourcedir
        }
    
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
