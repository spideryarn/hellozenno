import pytest
from playwright.sync_api import Page
from flask import Flask
from tests.backend.conftest import fixture_for_testing_db, MODELS
from utils.db_connection import init_db

FLASK_TEST_PORT = 3001


@pytest.fixture(scope="session")
def app(fixture_for_testing_db):
    """Create test Flask app."""
    app = Flask("app")
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_key"

    # Initialize database with test database
    init_db(app, fixture_for_testing_db)

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

    app.register_blueprint(views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(flashcard_views_bp)

    return app


@pytest.fixture(scope="session")
def base_url(app):
    """Get base URL for tests."""
    return f"http://localhost:{FLASK_TEST_PORT}"


@pytest.fixture(autouse=True)
def run_app(app, base_url):
    """Run the Flask app in a separate thread."""
    from threading import Thread
    import time

    server = Thread(target=lambda: app.run(port=FLASK_TEST_PORT))
    server.daemon = True
    server.start()

    # Give the server a moment to start
    time.sleep(1)

    yield

    # Server will be killed automatically since it's a daemon thread
