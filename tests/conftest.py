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
    SAMPLE_LEMMA_DATA,
    SAMPLE_PHRASE_DATA,
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
    app = Flask("app", root_path=os.path.dirname(os.path.dirname(__file__)))
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


@pytest.fixture(autouse=True)
def mock_gpt_from_template(monkeypatch):
    """Mock generate_gpt_from_template to avoid actual API calls."""

    def mock_generate(*args, **kwargs):
        if kwargs.get("prompt_template_var") == "extract_text_from_image":
            return "Test text in Greek", {}
        elif kwargs.get("prompt_template_var") == "translate_to_english":
            return "Test text in English", {}
        elif kwargs.get("prompt_template_var") == "extract_tricky_wordforms":
            return {
                "wordforms": [
                    {
                        "wordform": "test",
                        "lemma": "test",
                        "translated_word": "test",
                        "translations": ["test"],
                        "part_of_speech": "noun",
                        "inflection_type": "nominative",
                        "centrality": 0.8,
                    }
                ]
            }, {}
        elif kwargs.get("prompt_template_var") == "extract_phrases_from_text":
            return {
                "phrases": [
                    {
                        "canonical_form": SAMPLE_PHRASE_DATA["canonical_form"],
                        "raw_forms": SAMPLE_PHRASE_DATA["raw_forms"],
                        "translations": SAMPLE_PHRASE_DATA["translations"],
                        "part_of_speech": SAMPLE_PHRASE_DATA["part_of_speech"],
                        "register": SAMPLE_PHRASE_DATA["register"],
                        "commonality": SAMPLE_PHRASE_DATA["commonality"],
                        "guessability": SAMPLE_PHRASE_DATA["guessability"],
                        "etymology": SAMPLE_PHRASE_DATA["etymology"],
                        "cultural_context": SAMPLE_PHRASE_DATA["cultural_context"],
                        "mnemonics": SAMPLE_PHRASE_DATA["mnemonics"],
                        "component_words": SAMPLE_PHRASE_DATA["component_words"],
                        "usage_notes": SAMPLE_PHRASE_DATA["usage_notes"],
                        "difficulty_level": SAMPLE_PHRASE_DATA["difficulty_level"],
                    }
                ],
                "source": {
                    "txt_tgt": "Test text in Greek",
                },
            }, {}
        elif kwargs.get("prompt_template_var") == "metadata_for_lemma_full":
            # Use SAMPLE_LEMMA_DATA for realistic test data
            return SAMPLE_LEMMA_DATA, {}
        return "Unexpected template", {}

    monkeypatch.setattr("vocab_llm_utils.generate_gpt_from_template", mock_generate)
    monkeypatch.setattr("gdutils.llm_utils.generate_gpt_from_template", mock_generate)
