"""Shared test fixtures and configuration."""

import os

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
)
from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    create_complete_test_data,
)
from views.views import views_bp
from views.wordform_views import wordform_views_bp
from views.lemma_views import lemma_views_bp
from views.sourcedir_views import sourcedir_views_bp
from views.sourcefile_views import sourcefile_views_bp
from views.phrase_views import phrase_views_bp
from views.sentence_views import sentence_views_bp
from views.api import api_bp
from tests.mocks.search_mocks import mock_quick_search_for_wordform
from utils.db_connection import init_db
from views.flashcard_views import flashcard_views_bp
from utils.env_config import (
    POSTGRES_DB_NAME,
    POSTGRES_DB_USER,
    POSTGRES_DB_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
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
]


@pytest.fixture(scope="session", autouse=True)
def ensure_test_config():
    """Load and validate test configuration."""
    # Verify we're in test mode
    assert is_testing(), "Tests must be run with pytest"

    # Safety checks for test database
    assert POSTGRES_DB_NAME.endswith(
        "_test"
    ), f"Test database name must end with '_test', got {POSTGRES_DB_NAME}"
    assert POSTGRES_HOST == "localhost", "Test database host must be localhost"


@pytest.fixture(scope="session")
def fixture_for_testing_db():
    """Create a test database connection."""
    database = PostgresqlExtDatabase(
        POSTGRES_DB_NAME,
        user=POSTGRES_DB_USER,
        password=POSTGRES_DB_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )

    # Bind models to database
    for model in MODELS:
        model._meta.database = database

    # Create tables
    database.connect()
    database.create_tables(MODELS)

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
    app.register_blueprint(views_bp)
    app.register_blueprint(wordform_views_bp)
    app.register_blueprint(lemma_views_bp)
    app.register_blueprint(sourcedir_views_bp)
    app.register_blueprint(sourcefile_views_bp)
    app.register_blueprint(phrase_views_bp)
    app.register_blueprint(sentence_views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(flashcard_views_bp)

    with app.test_client() as client:
        yield client
