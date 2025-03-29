from unittest.mock import patch

from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    create_test_lemma,
    create_test_wordform,
)
from tests.backend.utils_for_testing import build_url_with_query
from views.wordform_views import get_wordform_metadata_vw
from views.languages_views import languages_list_vw
from views.search_views import search_landing_vw
from views.sourcedir_views import sourcedirs_for_language_vw


"""
Edge case tests for views, using the test database.
"""


def test_wordform_details(client, fixture_for_testing_db):
    """Test viewing details of a wordform."""
    # Create test data
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)

    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform=wordform.wordform,
    )
    response = client.get(url)
    assert response.status_code == 200
    data = response.data.decode()
    assert wordform.wordform in data
    assert wordform.translations[0] in data


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_nonexistent_wordform(mock_search, client):
    """Test viewing details of a nonexistent wordform."""
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="nonexistent",
    )
    response = client.get(url)
    assert response.status_code == 200
    data = response.data.decode()
    # Now search for 'Search Results' which is in the template
    assert "Search Results" in data
    assert "test" in data  # from mock possible_misspellings


def test_sourcedir_view_smoke_test(client):
    """Test that sourcedir views return 200 OK."""
    url = build_url_with_query(
        client, sourcedirs_for_language_vw, target_language_code=TEST_LANGUAGE_CODE
    )
    response = client.get(url)
    assert response.status_code == 200


def test_languages_view(client):
    """Test that languages view returns 200 OK."""
    url = build_url_with_query(client, languages_list_vw)
    response = client.get(url)
    assert response.status_code == 200


def test_search_functionality(client):
    """Test search functionality."""
    # Test search landing page
    url = build_url_with_query(
        client, search_landing_vw, target_language_code=TEST_LANGUAGE_CODE
    )
    response = client.get(url)
    assert response.status_code == 200

    # Test search with query
    url = build_url_with_query(
        client,
        search_landing_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        query_params={"q": "test"},
    )
    response = client.get(url)  # Using test data from fixture
    assert response.status_code == 302  # Should redirect to wordform view


def test_favicon_with_trailing_slash(client):
    """Test that favicon.ico works even with a trailing slash."""
    # This URL doesn't use build_url_with_query since it's not a Flask view function
    # It's handled directly by Flask's send_from_directory
    response = client.get("/favicon.ico/")
    assert response.status_code == 200
    assert response.mimetype == "image/vnd.microsoft.icon"
