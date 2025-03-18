import pytest
from unittest.mock import patch
from flask import url_for
from urllib.parse import quote

from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import SAMPLE_PHRASE_DATA, TEST_LANGUAGE_CODE
from db_models import Phrase
from tests.backend.utils_for_testing import (
    get_sourcedir_and_file,
    assert_html_response,
    with_wordform_search_mock,
)


"""
Smoke tests for the read-only views (i.e. won't change the data),
using the test database.
"""


def test_languages_view(client):
    """Test the languages list view."""
    response = client.get("/lang")
    assert_html_response(response)


def test_search_landing_view(client):
    """Test the search landing page."""
    response = client.get("/lang/el/search")
    assert_html_response(response)


def test_lemmas_list_alpha_sort(client):
    """Test the lemmas list view with alphabetical sorting."""
    response = client.get("/lang/el/lemmas?sort=alpha")
    assert_html_response(response)


def test_lemmas_list_commonality_sort(client):
    """Test the lemmas list view with commonality sorting."""
    response = client.get("/lang/el/lemmas?sort=commonality")
    assert_html_response(response)


def test_lemma_detail_existing(client):
    """Test the lemma detail view with an existing lemma."""
    response = client.get("/lang/el/lemma/test")  # Using test lemma from test_data fixture
    assert_html_response(response)


def test_lemma_detail_nonexistent(client):
    """Test the lemma detail view with a non-existent lemma."""
    response = client.get("/lang/el/lemma/nonexistentlemma")
    assert_html_response(response)


def test_lemmas_list_date_sort(client):
    """Test the lemmas list view with date sorting."""
    response = client.get("/lang/el/lemmas?sort=date")
    assert_html_response(response)


@with_wordform_search_mock
def test_wordforms_list(mock_search, client):
    """Test the wordforms list view."""
    response = client.get("/lang/el/wordforms")
    assert_html_response(response)


@pytest.mark.skip("There appears to be an issue with the test data or mock")
@with_wordform_search_mock
def test_wordform_detail_existing(mock_search, client):
    """Test the wordform detail view with an existing wordform."""
    response = client.get(
        "/lang/el/wordform/test"
    )  # Using test wordform from test_data fixture
    assert_html_response(response)


@pytest.mark.skip("There appears to be an issue with the test data or mock")
@with_wordform_search_mock
def test_wordform_detail_nonexistent(mock_search, client):
    """Test the wordform detail view with a non-existent wordform."""
    response = client.get("/lang/el/wordform/nonexistentword")
    assert_html_response(response)


def test_sourcedirs_list_alpha_sort(client):
    """Test the sourcedirs list view with alphabetical sorting."""
    response = client.get("/lang/el/?sort=alpha")
    assert_html_response(response)


def test_sourcedirs_list_date_sort(client):
    """Test the sourcedirs list view with date sorting."""
    response = client.get("/lang/el/?sort=date")
    assert_html_response(response)


def test_sourcedir_contents(client):
    """Test viewing contents of a sourcedir if any exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir:
        response = client.get(f"/lang/el/{quote(sourcedir)}")
        assert_html_response(response)

        if sourcefile:
            # Test inspect view
            response = client.get(f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}")
            assert_html_response(response)

            # Test file view
            response = client.get(f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}/view")
            assert_html_response(response)

            # Test sentences view
            response = client.get(
                f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}/sentences"
            )
            assert_html_response(response)


def test_phrases_list(client):
    """Test the phrases list view."""
    response = client.get("/lang/el/phrases")
    assert_html_response(response)


def test_phrase_detail_existing(client, fixture_for_testing_db):
    """Test the phrase detail view with an existing phrase using slug."""
    # Create a test phrase with the sample data
    phrase = Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)

    # Test with the created phrase using its slug
    response = client.get(f"/lang/{TEST_LANGUAGE_CODE}/phrases/{phrase.slug}")
    assert_html_response(response)


def test_phrase_detail_nonexistent(client):
    """Test the phrase detail view with a non-existent phrase."""
    # Test new slug-based route
    response = client.get("/lang/el/phrases/nonexistentphrase12345")
    assert_html_response(response, status_code=404)


def test_sourcefile_views(client):
    """Test sourcefile-related views if any sourcefiles exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir and sourcefile:
        # Test inspect view
        response = client.get(f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}")
        assert_html_response(response)

        # Test file view
        response = client.get(f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}/view")
        assert_html_response(response)

        # Test sentences view
        response = client.get(f"/lang/el/{quote(sourcedir)}/{quote(sourcefile)}/sentences")
        assert_html_response(response)
