import pytest
from unittest.mock import patch
from flask import url_for

from test_utils import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    create_test_lemma,
    create_test_wordform,
)


"""
Edge case tests for views, using the test database.
"""


def test_wordform_details(client, test_db):
    """Test viewing details of a wordform."""
    # Create test data
    lemma = create_test_lemma(test_db)
    wordform = create_test_wordform(test_db, lemma)

    response = client.get(f"/{TEST_LANGUAGE_CODE}/wordform/{wordform.wordform}")
    assert response.status_code == 200
    data = response.data.decode()
    assert wordform.wordform in data
    assert wordform.translations[0] in data


@patch(
    "wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_nonexistent_wordform(mock_search, client):
    """Test viewing details of a nonexistent wordform."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/wordform/nonexistent")
    assert response.status_code == 200
    data = response.data.decode()
    assert "Invalid Word" in data
    assert "test" in data  # from mock possible_misspellings


def test_sourcedir_view_smoke_test(client):
    """Test that sourcedir views return 200 OK."""
    response = client.get(f"/{TEST_LANGUAGE_CODE}/")
    assert response.status_code == 200


def test_languages_view(client):
    """Test that languages view returns 200 OK."""
    response = client.get("/languages")
    assert response.status_code == 200


def test_search_functionality(client):
    """Test search functionality."""
    # Test search landing page
    response = client.get(f"/{TEST_LANGUAGE_CODE}/search")
    assert response.status_code == 200

    # Test search with query
    response = client.get(
        f"/{TEST_LANGUAGE_CODE}/search?q=test"
    )  # Using test data from fixture
    assert response.status_code == 302  # Should redirect to wordform view


def test_favicon_with_trailing_slash(client):
    """Test that favicon.ico works even with a trailing slash."""
    response = client.get("/favicon.ico/")
    assert response.status_code == 200
    assert response.mimetype == "image/vnd.microsoft.icon"
