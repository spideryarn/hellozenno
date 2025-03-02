import pytest
from unittest.mock import patch
from flask import url_for
from urllib.parse import quote

from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import SAMPLE_PHRASE_DATA, TEST_LANGUAGE_CODE
from db_models import Phrase


"""
Smoke tests for the read-only views (i.e. won't change the data),
using the test database.
"""


def test_languages_view(client):
    """Test the languages list view."""
    response = client.get("/languages")
    assert response.status_code == 200


def test_search_landing_view(client):
    """Test the search landing page."""
    response = client.get("/el/search")
    assert response.status_code == 200


def test_lemmas_list_alpha_sort(client):
    """Test the lemmas list view with alphabetical sorting."""
    response = client.get("/el/lemmas?sort=alpha")
    assert response.status_code == 200


def test_lemmas_list_commonality_sort(client):
    """Test the lemmas list view with commonality sorting."""
    response = client.get("/el/lemmas?sort=commonality")
    assert response.status_code == 200


def test_lemma_detail_existing(client):
    """Test the lemma detail view with an existing lemma."""
    response = client.get("/el/lemma/test")  # Using test lemma from test_data fixture
    assert response.status_code == 200


def test_lemma_detail_nonexistent(client):
    """Test the lemma detail view with a non-existent lemma."""
    response = client.get("/el/lemma/nonexistentlemma")
    assert response.status_code == 200


def test_lemmas_list_date_sort(client):
    """Test the lemmas list view with date sorting."""
    response = client.get("/el/lemmas?sort=date")
    assert response.status_code == 200


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_wordforms_list(mock_search, client):
    """Test the wordforms list view."""
    response = client.get("/el/wordforms")
    assert response.status_code == 200


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_wordform_detail_existing(mock_search, client):
    """Test the wordform detail view with an existing wordform."""
    response = client.get(
        "/el/wordform/test"
    )  # Using test wordform from test_data fixture
    assert response.status_code == 200


@patch(
    "views.wordform_views.quick_search_for_wordform",
    side_effect=mock_quick_search_for_wordform,
)
def test_wordform_detail_nonexistent(mock_search, client):
    """Test the wordform detail view with a non-existent wordform."""
    response = client.get("/el/wordform/nonexistentword")
    assert response.status_code == 200


def test_sourcedirs_list_alpha_sort(client):
    """Test the sourcedirs list view with alphabetical sorting."""
    response = client.get("/el/?sort=alpha")
    assert response.status_code == 200


def test_sourcedirs_list_date_sort(client):
    """Test the sourcedirs list view with date sorting."""
    response = client.get("/el/?sort=date")
    assert response.status_code == 200


def test_sourcedir_contents(client):
    """Test viewing contents of a sourcedir if any exist."""
    # First get the list of sourcedirs
    response = client.get("/el/")
    assert response.status_code == 200

    # Only test if we have sourcedirs
    if "data-sourcedir" in response.data.decode():
        html = response.data.decode()
        start = html.find('data-sourcedir="') + len('data-sourcedir="')
        end = html.find('"', start)
        sourcedir = html[start:end]

        response = client.get(f"/el/{quote(sourcedir)}")
        assert response.status_code == 200

        # Only test if we have sourcefiles
        if "data-sourcefile" in response.data.decode():
            html = response.data.decode()
            start = html.find('data-sourcefile="') + len('data-sourcefile="')
            end = html.find('"', start)
            sourcefile = html[start:end]

            # Test inspect view
            response = client.get(f"/el/{quote(sourcedir)}/{quote(sourcefile)}")
            assert response.status_code == 200

            # Test file view
            response = client.get(f"/el/{quote(sourcedir)}/{quote(sourcefile)}/view")
            assert response.status_code == 200

            # Test sentences view
            response = client.get(
                f"/el/{quote(sourcedir)}/{quote(sourcefile)}/sentences"
            )
            assert response.status_code == 200


def test_phrases_list(client):
    """Test the phrases list view."""
    response = client.get("/el/phrases")
    assert response.status_code == 200
    # Check that we got a valid HTML response
    assert "text/html" in response.content_type


def test_phrase_detail_existing(client, fixture_for_testing_db):
    """Test the phrase detail view with an existing phrase using slug."""
    # Create a test phrase with the sample data
    phrase = Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)

    # Test with the created phrase using its slug
    response = client.get(f"/{TEST_LANGUAGE_CODE}/phrases/{phrase.slug}")
    assert response.status_code == 200
    # Check that we got a valid HTML response
    assert "text/html" in response.content_type


def test_phrase_detail_nonexistent(client):
    """Test the phrase detail view with a non-existent phrase."""
    # Test new slug-based route
    response = client.get("/el/phrases/nonexistentphrase12345")
    assert response.status_code == 404


def test_sourcefile_views(client):
    """Test sourcefile-related views if any sourcefiles exist."""
    # First get the list of sourcedirs
    response = client.get("/el/")
    assert response.status_code == 200

    # Only test if we have sourcedirs
    if "data-sourcedir" in response.data.decode():
        html = response.data.decode()
        start = html.find('data-sourcedir="') + len('data-sourcedir="')
        end = html.find('"', start)
        sourcedir = html[start:end]

        # Get sourcedir contents
        response = client.get(f"/el/{quote(sourcedir)}")
        assert response.status_code == 200

        # Only test if we have sourcefiles
        if "data-sourcefile" in response.data.decode():
            html = response.data.decode()
            start = html.find('data-sourcefile="') + len('data-sourcefile="')
            end = html.find('"', start)
            sourcefile = html[start:end]

            # Test inspect view
            response = client.get(f"/el/{quote(sourcedir)}/{quote(sourcefile)}")
            assert response.status_code == 200

            # Test file view
            response = client.get(f"/el/{quote(sourcedir)}/{quote(sourcefile)}/view")
            assert response.status_code == 200

            # Test sentences view
            response = client.get(
                f"/el/{quote(sourcedir)}/{quote(sourcefile)}/sentences"
            )
            assert response.status_code == 200
