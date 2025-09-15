"""Shared test fixtures and configuration."""

import os
from urllib.parse import urlparse

# This has to come at the top, before we import config variables
# from `env_config` below, so that `PYTEST_CURRENT_TEST` has already been
# set before `env_config.is_testing()` runs
os.environ["PYTEST_CURRENT_TEST"] = "1"

import pytest
from pathlib import Path
from playhouse.postgres_ext import PostgresqlExtDatabase
from flask import Flask

from db_models import (
    Lemma,
    Wordform,
    Sentence,
    SentenceLemma,
    Phrase,
    LemmaExampleSentence,
    PhraseExampleSentence,
    RelatedPhrase,
    Sourcedir,
    Sourcefile,
    SourcefileWordform,
    SourcefilePhrase,
    Profile,
    UserLemma,
)
from tests.fixtures_for_tests import (
    TEST_TARGET_LANGUAGE_CODE,
    create_complete_test_data,
)
from views.core_views import core_views_bp
from views.wordform_views import wordform_views_bp
from views.lemma_views import lemma_views_bp
from views.sourcedir_views import sourcedir_views_bp
from views.sourcefile_views import sourcefile_views_bp
from views.phrase_views import phrase_views_bp
from views.sentence_views import sentence_views_bp
from views.search_views import search_views_bp
from views.auth_views import auth_views_bp
from views.system_views import system_views_bp
from views.languages_views import languages_views_bp

# Commented out missing API blueprint
# from views.core_api import core_api_bp
from views.wordform_api import wordform_api_bp
from views.lemma_api import lemma_api_bp
from views.phrase_api import phrase_api_bp
from views.sourcedir_api import sourcedir_api_bp
from views.sourcefile_api import sourcefile_api_bp
from views.sentence_api import sentence_api_bp
from tests.mocks.search_mocks import mock_quick_search_for_wordform
from utils.db_connection import init_db
from views.flashcard_views import flashcard_views_bp
from utils.env_config import (
    DATABASE_URL,
    is_testing,
)

# All models in dependency order for table creation/deletion
MODELS = [
    Lemma,
    Wordform,
    Sentence,
    SentenceLemma,
    Phrase,
    LemmaExampleSentence,
    PhraseExampleSentence,
    RelatedPhrase,
    Sourcedir,
    Sourcefile,
    SourcefileWordform,
    SourcefilePhrase,
    Profile,
    UserLemma,
]


@pytest.fixture(scope="session", autouse=True)
def ensure_test_config():
    """Load and validate test configuration."""
    # Verify we're in test mode
    assert is_testing(), "Tests must be run with pytest"

    # Parse DATABASE_URL
    db_url = urlparse(DATABASE_URL.get_secret_value())

    # Safety checks for test database
    assert db_url.path.endswith(
        "_test"
    ), f"Test database name must end with '_test', got {db_url.path}"
    assert db_url.hostname == "localhost", "Test database host must be localhost"


@pytest.fixture(scope="session")
def fixture_for_testing_db():
    """Create a test database connection."""
    # Parse DATABASE_URL
    db_url = urlparse(DATABASE_URL.get_secret_value())

    database = PostgresqlExtDatabase(
        db_url.path.lstrip("/"),  # Remove leading slash from path to get database name
        user=db_url.username,
        password=db_url.password,
        host=db_url.hostname,
        port=db_url.port or 5432,  # Default to 5432 if port not specified
    )

    # Bind models to database
    for model in MODELS:
        model._meta.database = database

    # Create tables
    database.connect()

    # Ensure Supabase auth schema and minimal users table exist for FK references
    try:
        database.execute_sql("CREATE SCHEMA IF NOT EXISTS auth;")
        database.execute_sql(
            """
            CREATE TABLE IF NOT EXISTS auth.users (
                id UUID PRIMARY KEY,
                email TEXT
            );
            """
        )
    except Exception:
        # If running on an engine without schema support, ignore
        pass

    # Drop tables if they exist and recreate them to ensure schema is up-to-date
    database.drop_tables(MODELS, safe=True, cascade=True)
    database.create_tables(MODELS)

    # Ensure a dummy auth user exists matching the test g.user_id used in fixtures
    try:
        database.execute_sql(
            """
            INSERT INTO auth.users (id, email)
            VALUES ('00000000-0000-0000-0000-000000000000', 'test@example.com')
            ON CONFLICT (id) DO NOTHING;
            """
        )
    except Exception:
        pass

    yield database

    # Cleanup
    database.close()


@pytest.fixture(autouse=True)
def clean_tables(fixture_for_testing_db):
    """Clean all tables between tests using TRUNCATE."""
    with fixture_for_testing_db.atomic():
        fixture_for_testing_db.execute_sql(
            "TRUNCATE TABLE {} CASCADE".format(
                ", ".join(f'"{model._meta.table_name}"' for model in reversed(MODELS))
            )
        )
    yield


@pytest.fixture
def test_data(fixture_for_testing_db):
    """Create test data in the database."""
    return create_complete_test_data(fixture_for_testing_db)


@pytest.fixture
def client(fixture_for_testing_db):
    """Create a test client with database connection."""
    app = Flask(
        "app", root_path=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_key"

    # Initialize database
    init_db(app, fixture_for_testing_db)

    # Register blueprints
    app.register_blueprint(core_views_bp)
    app.register_blueprint(languages_views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(search_views_bp)
    app.register_blueprint(auth_views_bp)
    app.register_blueprint(system_views_bp)
    app.register_blueprint(flashcard_views_bp)
    # Register API blueprints
    # Commented out missing API blueprint
    # app.register_blueprint(core_api_bp)
    app.register_blueprint(wordform_api_bp)
    app.register_blueprint(lemma_api_bp)
    app.register_blueprint(phrase_api_bp)
    app.register_blueprint(sourcedir_api_bp)
    app.register_blueprint(sourcefile_api_bp)
    app.register_blueprint(sentence_api_bp)

    # Register custom context processors for testing
    from utils.url_registry import endpoint_for, generate_route_registry

    # Create route registry for tests
    with app.app_context():
        route_registry = generate_route_registry(app)

        @app.context_processor
        def inject_routes():
            """Make route registry available to all templates."""
            return {
                "route_registry": route_registry,
                "endpoint_for": endpoint_for,  # Make endpoint_for available in all templates
            }

        # Create our own minimal function that matches production
        @app.context_processor
        def inject_base_view_functions():
            """Inject minimal view functions needed by the base template.

            This matches the function in api/index.py without importing it directly.
            """
            from views.languages_views import languages_list_vw
            from views.search_views import search_landing_vw

            return {
                # Only the functions required by base.jinja
                "languages_list_vw": languages_list_vw,
                "search_landing_vw": search_landing_vw,
            }

    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def bypass_api_auth(monkeypatch, client):
    """Bypass API auth for tests that don't care about authentication.

    Sets a dummy user and profile so @api_auth_required passes without touching DB or external services.
    """
    from utils import auth_utils

    def fake_attempt():
        from flask import g
        g.user = {"id": "00000000-0000-0000-0000-000000000000", "email": "test@example.com"}
        g.user_id = g.user["id"]
        # Non-None sentinel to satisfy decorator checks without DB
        g.profile = {"id": 1}
        return True

    monkeypatch.setattr(auth_utils, "_attempt_authentication_and_set_g", fake_attempt)

    # Also ensure g is set for every request served by the test client
    @client.application.before_request
    def _inject_test_user():
        from flask import g as _g
        _g.user = {"id": "00000000-0000-0000-0000-000000000000", "email": "test@example.com"}
        _g.user_id = _g.user["id"]
        _g.profile = {"id": 1}


# Note: Avoid pushing a global app or request context here to prevent teardown conflicts


@pytest.fixture(autouse=True)
def mock_tts_autouse(monkeypatch):
    """Mock ElevenLabs TTS globally so tests never hit the network."""

    def _fake_outloud(*args, **kwargs):
        mp3_filen = kwargs.get("mp3_filen")
        if mp3_filen:
            with open(mp3_filen, "wb") as f:
                f.write(b"test audio data")

    monkeypatch.setattr(
        "gjdutils.outloud_text_to_speech.outloud_elevenlabs", _fake_outloud
    )
