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
from env_config import getenv

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

TEST_DB_NAME = "hellozenno_test"


@pytest.fixture(scope="session", autouse=True)
def ensure_test_config():
    """Load and validate test configuration."""
    load_dotenv(".env.testing", override=True)

    # Safety checks for test database
    db_name = getenv("POSTGRES_DB_NAME")
    assert db_name.endswith(
        "_test"
    ), f"Test database name must end with '_test', got {db_name}"
    assert (
        getenv("POSTGRES_HOST") == "localhost"
    ), "Test database host must be localhost"
    assert (
        getenv("POSTGRES_PORT", PositiveInt) == 5432
    ), "Test database port must be 5432"


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the test session."""
    # Connect to postgres db to create test db
    conn = psycopg2.connect(
        dbname="postgres",
        user=getenv("POSTGRES_DB_USER"),
        password=getenv("POSTGRES_DB_PASSWORD"),
        host=getenv("POSTGRES_HOST"),
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create test database
    TEST_DB_NAME = getenv("POSTGRES_DB_NAME")
    cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
    cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    cur.close()
    conn.close()

    # Configure the test database
    database = PostgresqlExtDatabase(
        TEST_DB_NAME,
        user=getenv("POSTGRES_DB_USER"),
        password=getenv("POSTGRES_DB_PASSWORD"),
        host=getenv("POSTGRES_HOST"),
        port=getenv("POSTGRES_PORT", PositiveInt),
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
        user=getenv("POSTGRES_DB_USER"),
        password=getenv("POSTGRES_DB_PASSWORD"),
        host=getenv("POSTGRES_HOST"),
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
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
