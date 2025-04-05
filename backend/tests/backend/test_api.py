import pytest
from db_models import Lemma, Wordform
from tests.fixtures_for_tests import TEST_LANGUAGE_CODE, SAMPLE_LEMMA_DATA
from tests.backend.utils_for_testing import build_url_with_query


def test_word_preview(client, fixture_for_testing_db):
    """Test the word preview API endpoint."""
    # Create test data
    with fixture_for_testing_db.bind_ctx([Lemma, Wordform]):
        lemma = Lemma.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_LEMMA_DATA)
        wordform = Wordform.create(
            wordform="preview_testing",
            language_code=TEST_LANGUAGE_CODE,
            lemma_entry=lemma,
            translations=["testing translation"],
        )

        # Test existing word
        from views.wordform_api import word_preview_api

        url = build_url_with_query(
            client,
            word_preview_api,
            target_language_code=TEST_LANGUAGE_CODE,
            word="preview_testing",
        )
        response = client.get(url)
        assert response.status_code == 200
        data = response.get_json()
        assert data["lemma"] == SAMPLE_LEMMA_DATA["lemma"]
        assert data["translation"] == "testing translation"
        assert data["etymology"] == SAMPLE_LEMMA_DATA["etymology"]
        assert "Cache-Control" in response.headers
        assert "max-age=60" in response.headers["Cache-Control"]

        # Test nonexistent word
        from views.wordform_api import word_preview_api

        url = build_url_with_query(
            client,
            word_preview_api,
            target_language_code=TEST_LANGUAGE_CODE,
            word="nonexistent",
        )
        response = client.get(url)
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "Not Found"
        assert "description" in data
        assert "not found" in data["description"]
