"""Shared test fixtures and configuration."""

import pytest
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from playhouse.postgres_ext import PostgresqlExtDatabase
from flask import Flask
import os
from dotenv import load_dotenv
from pydantic import StrictStr, PositiveInt

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
from views import views_bp
from wordform_views import wordform_views_bp
from lemma_views import lemma_views_bp
from sourcedir_views import sourcedir_views_bp
from sourcefile_views import sourcefile_views_bp
from phrase_views import phrase_views_bp
from sentence_views import sentence_views_bp
from api import api_bp
from test_utils import mock_quick_search_for_wordform
from db_connection import init_db
from flashcard_views import flashcard_views_bp
from env_config import (
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
    assert POSTGRES_PORT == 5432, "Test database port must be 5432"


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the test session."""
    # Connect to postgres db to create test db
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_DB_USER,
        password=POSTGRES_DB_PASSWORD,
        host=POSTGRES_HOST,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create test database
    cur.execute(f'DROP DATABASE IF EXISTS "{POSTGRES_DB_NAME}"')
    cur.execute(f'CREATE DATABASE "{POSTGRES_DB_NAME}"')
    cur.close()
    conn.close()

    # Configure the test database
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

    # Cleanup after all tests
    database.drop_tables(MODELS)
    database.close()

    # Drop test database
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_DB_USER,
        password=POSTGRES_DB_PASSWORD,
        host=POSTGRES_HOST,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS "{POSTGRES_DB_NAME}"')
    cur.close()
    conn.close()


@pytest.fixture(autouse=True)
def clean_tables(test_db):
    """Clean all tables between tests using TRUNCATE."""
    with test_db.atomic():
        test_db.execute_sql(
            "TRUNCATE TABLE {} CASCADE".format(
                ", ".join(f'"{model._meta.table_name}"' for model in reversed(MODELS))
            )
        )
    yield


@pytest.fixture
def test_data(test_db):
    """Create test data in the database."""
    return create_complete_test_data(test_db)


@pytest.fixture
def client(test_db):
    """Create a test client with database connection."""
    app = Flask("app", root_path=os.path.dirname(os.path.dirname(__file__)))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_key"

    # Initialize database
    init_db(app, test_db)

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
