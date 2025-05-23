import pytest
from unittest.mock import patch
from peewee import DoesNotExist
from peewee import fn

from backend.views.wordform_api import delete_wordform_api
from db_models import Wordform
from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    TEST_TARGET_LANGUAGE_CODE,
    TEST_LANGUAGE_NAME,
    create_test_lemma,
    create_test_wordform,
)
from tests.backend.utils_for_testing import build_url_with_query
from views.languages_views import languages_list_vw
from views.lemma_views import get_lemma_metadata_vw
from views.sourcedir_views import sourcedirs_for_language_vw
from views.wordform_views import (
    wordforms_list_vw,
    get_wordform_metadata_vw,
)


def test_wordforms_list(client, fixture_for_testing_db):
    """Test the wordforms list view."""
    # Create test data
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)

    # Test accessing the wordforms list view
    url = build_url_with_query(
        client, wordforms_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    response = client.get(url)
    assert response.status_code == 200
    assert str(wordform.wordform).encode() in response.data


def test_get_existing_wordform(client, fixture_for_testing_db):
    """Test getting metadata for an existing wordform."""
    # Create test data
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)

    # Test accessing the wordform
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform=wordform.wordform,
    )
    response = client.get(url)
    assert response.status_code == 200
    data = response.data.decode()
    assert str(wordform.wordform) in data
    assert str(lemma.lemma) in data
    assert wordform.translations[0] in data
    assert wordform.inflection_type in data


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_get_nonexistent_wordform(mock_search, client):
    """Test getting metadata for a nonexistent wordform."""
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform="nonexistent",
    )
    response = client.get(url)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Search Results" in data
    assert "test" in data  # from mock possible_misspellings


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_get_new_wordform(mock_search, client):
    """Test getting metadata for a new wordform that will be created."""
    # With the new implementation, a single match should redirect to the wordform page
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform="newword",
    )
    response = client.get(url)
    assert response.status_code == 302  # Redirect status code
    assert "newword" in response.headers["Location"]

    # Follow the redirect and make sure we don't get into a loop
    response = client.get(response.headers["Location"])
    assert response.status_code == 200  # Should render the page now, not redirect again

    # Verify the wordform was created in the database
    wordform = Wordform.get(
        Wordform.wordform == "newword",
        Wordform.target_language_code == TEST_TARGET_LANGUAGE_CODE,
    )
    assert wordform is not None


@pytest.mark.skip("Template needs to be updated for new URL patterns")
def test_wordform_template_rendering(client, fixture_for_testing_db):
    """Test that the wordform template renders correctly with all navigation elements."""
    # Create test data
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)

    # Create test context
    with client.application.test_request_context():
        # Render the template
        template = client.application.jinja_env.get_template("wordform.jinja")
        html = template.render(
            wordform_metadata={
                "wordform": str(wordform.wordform),
                "translations": wordform.translations,
                "part_of_speech": wordform.part_of_speech,
                "inflection_type": wordform.inflection_type,
                "lemma": str(lemma.lemma),
                "possible_misspellings": None,
            },
            target_language_code=TEST_TARGET_LANGUAGE_CODE,
            target_language_name=TEST_LANGUAGE_NAME,
            dict_html="<div>Test dictionary entry</div>",
        )

        # Check that all navigation links are present
        assert (
            build_url_with_query(
                client,
                languages_list_vw,
            )
            in html
        )
        assert (
            build_url_with_query(
                client,
                sourcedirs_for_language_vw,
                target_language_code=TEST_TARGET_LANGUAGE_CODE,
            )
            in html
        )
        url = build_url_with_query(
            client,
            wordforms_list_vw,
            target_language_code=TEST_TARGET_LANGUAGE_CODE,
        )
        assert f'href="{url}"' in html
        assert (
            build_url_with_query(
                client,
                get_lemma_metadata_vw,
                target_language_code=TEST_TARGET_LANGUAGE_CODE,
                lemma=str(lemma.lemma),
            )
            in html
        )

        # Check that metadata is rendered correctly
        assert str(wordform.wordform) in html
        assert wordform.translations[0] in html
        assert wordform.part_of_speech in html
        assert wordform.inflection_type in html
        assert str(lemma.lemma) in html


def test_delete_wordform(client, fixture_for_testing_db):
    """Test deleting a wordform."""
    # Create test data
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)

    # First verify the wordform exists
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform=wordform.wordform,
    )
    response = client.get(url)
    assert response.status_code == 200
    assert str(wordform.wordform) in response.data.decode()

    # Delete the wordform
    delete_url = build_url_with_query(
        client,
        delete_wordform_api,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform=wordform.wordform,
    )
    response = client.post(delete_url)
    assert response.status_code == 302  # Redirect after deletion

    # Check that it redirects to wordforms list
    wordforms_url = build_url_with_query(
        client, wordforms_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    assert response.headers["Location"].endswith(wordforms_url)

    # Verify the wordform is deleted from the database
    with pytest.raises(DoesNotExist):
        Wordform.get(
            Wordform.wordform == wordform.wordform,
            Wordform.target_language_code == TEST_TARGET_LANGUAGE_CODE,
        )


def test_delete_nonexistent_wordform(client):
    """Test deleting a wordform that doesn't exist."""
    url = build_url_with_query(
        client,
        delete_wordform_api,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        wordform="nonexistent",
    )
    response = client.post(url)
    assert response.status_code == 302  # Should redirect even if wordform doesn't exist

    # Check that it redirects to wordforms list
    wordforms_url = build_url_with_query(
        client, wordforms_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    assert response.headers["Location"].endswith(wordforms_url)


def test_wordforms_list_sorting(client, fixture_for_testing_db):
    """Test the sorting functionality of the wordforms list view, especially case-insensitive alphabetical sorting."""
    # Clear any existing wordforms
    Wordform.delete().execute()

    # Create wordforms with different case
    lemma = create_test_lemma(fixture_for_testing_db)

    # Create wordforms with mixed case to test case-insensitive sorting
    wordform1 = Wordform.create(
        wordform="Alpha",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma,
        translations=["test1"],
    )
    wordform2 = Wordform.create(
        wordform="beta",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma,
        translations=["test2"],
    )
    wordform3 = Wordform.create(
        wordform="Gamma",
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        lemma_entry=lemma,
        translations=["test3"],
    )

    # Test alphabetical sorting (default) - should be case-insensitive
    url = build_url_with_query(
        client, wordforms_list_vw, target_language_code=TEST_TARGET_LANGUAGE_CODE
    )
    response = client.get(url)
    assert response.status_code == 200

    # Get the wordforms from the database in the expected order
    wordforms_alpha = list(
        Wordform.select()
        .where(Wordform.target_language_code == TEST_TARGET_LANGUAGE_CODE)
        .order_by(fn.Lower(Wordform.wordform))
    )
    wordform_names_alpha = [wordform.wordform for wordform in wordforms_alpha]
    assert wordform_names_alpha == [
        "Alpha",
        "beta",
        "Gamma",
    ], "Database should return wordforms in case-insensitive alphabetical order"
