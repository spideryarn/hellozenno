import pytest
from unittest.mock import patch
from flask import url_for
from urllib.parse import quote

from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    SAMPLE_PHRASE_DATA,
    TEST_LANGUAGE_CODE,
    create_complete_test_data,
)
from db_models import Phrase
from tests.backend.utils_for_testing import (
    get_sourcedir_and_file,
    assert_html_response,
    with_wordform_search_mock,
    build_url_with_query,
)
from utils.url_registry import endpoint_for

# Import all view functions that we'll need
from views.core_views import languages_vw
from views.search_views import search_landing_vw
from views.lemma_views import lemmas_list_vw, get_lemma_metadata_vw
from views.wordform_views import wordforms_list_vw, get_wordform_metadata_vw
from views.phrase_views import phrases_list_vw, get_phrase_metadata_vw
from views.sourcedir_views import sourcedirs_for_language_vw, sourcefiles_for_sourcedir_vw
from views.sourcefile_views import inspect_sourcefile_vw, inspect_sourcefile_text_vw, sourcefile_sentences_vw


"""
Smoke tests for the read-only views (i.e. won't change the data),
using the test database.
"""


def test_languages_view(client):
    """Test the languages list view."""
    url = build_url_with_query(client, languages_vw)
    response = client.get(url)
    assert_html_response(response)


def test_language_view(client):
    """Test the search landing page."""
    url = build_url_with_query(client, sourcedirs_for_language_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_search_landing_view(client):
    """Test the search landing page."""
    url = build_url_with_query(client, search_landing_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_alpha_sort(client):
    """Test the lemmas list view with alphabetical sorting."""
    url = build_url_with_query(client, lemmas_list_vw, query_params={"sort": "alpha"}, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_commonality_sort(client):
    """Test the lemmas list view with commonality sorting."""
    url = build_url_with_query(client, lemmas_list_vw, query_params={"sort": "commonality"}, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_lemma_detail_existing(client, fixture_for_testing_db):
    """Test the lemma detail view with an existing lemma."""
    # Create test data for this specific test
    test_data = create_complete_test_data(fixture_for_testing_db)
    lemma = test_data["lemma"]
    url = build_url_with_query(client, get_lemma_metadata_vw, target_language_code="el", lemma=lemma.lemma)
    response = client.get(url)
    assert_html_response(response)


def test_lemma_detail_nonexistent(client):
    """Test the lemma detail view with a non-existent lemma."""
    url = build_url_with_query(client, get_lemma_metadata_vw, target_language_code="el", lemma="nonexistentlemma")
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_date_sort(client):
    """Test the lemmas list view with date sorting."""
    url = build_url_with_query(client, lemmas_list_vw, query_params={"sort": "date"}, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


@with_wordform_search_mock
def test_wordforms_list(mock_search, client, fixture_for_testing_db):
    """Test the wordforms list view."""
    url = build_url_with_query(client, wordforms_list_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


@with_wordform_search_mock
def test_wordform_detail_existing(mock_search, client, fixture_for_testing_db):
    """Test the wordform detail view with an existing wordform."""
    # Create test data including a wordform
    test_data = create_complete_test_data(fixture_for_testing_db)
    wordform = test_data["wordform"]
    
    url = build_url_with_query(client, get_wordform_metadata_vw, target_language_code="el", wordform=wordform.wordform)
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


@with_wordform_search_mock
def test_wordform_detail_nonexistent(mock_search, client):
    """Test the wordform detail view with a non-existent wordform."""
    url = build_url_with_query(client, get_wordform_metadata_vw, target_language_code="el", wordform="nonexistentword")
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


def test_sourcedirs_list_alpha_sort(client):
    """Test the sourcedirs list view with alphabetical sorting."""
    url = build_url_with_query(client, sourcedirs_for_language_vw, query_params={"sort": "alpha"}, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_sourcedirs_list_date_sort(client):
    """Test the sourcedirs list view with date sorting."""
    url = build_url_with_query(client, sourcedirs_for_language_vw, query_params={"sort": "date"}, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_sourcedir_contents(client):
    """Test viewing contents of a sourcedir if any exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir:
        url = build_url_with_query(client, sourcefiles_for_sourcedir_vw, 
                                  target_language_code="el", 
                                  sourcedir_slug=sourcedir)
        response = client.get(url)
        assert_html_response(response)

        if sourcefile:
            # Test inspect view
            url = build_url_with_query(client, inspect_sourcefile_vw,
                                      target_language_code="el",
                                      sourcedir_slug=sourcedir,
                                      sourcefile_slug=sourcefile)
            response = client.get(url)
            assert_html_response(response)

            # Test file text view
            url = build_url_with_query(client, inspect_sourcefile_text_vw,
                                      target_language_code="el",
                                      sourcedir_slug=sourcedir,
                                      sourcefile_slug=sourcefile)
            response = client.get(url)
            assert_html_response(response)

            # Test sentences view
            url = build_url_with_query(client, sourcefile_sentences_vw,
                                      target_language_code="el",
                                      sourcedir_slug=sourcedir,
                                      sourcefile_slug=sourcefile)
            response = client.get(url)
            assert_html_response(response)


def test_phrases_list(client, fixture_for_testing_db):
    """Test the phrases list view."""
    # Create test data for this specific test
    test_data = create_complete_test_data(fixture_for_testing_db)
    url = build_url_with_query(client, phrases_list_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_phrase_detail_existing(client, fixture_for_testing_db):
    """Test the phrase detail view with an existing phrase using slug."""
    # Create a test phrase with the sample data
    phrase = Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)

    # Test with the created phrase using its slug
    url = build_url_with_query(client, get_phrase_metadata_vw, 
                              target_language_code=TEST_LANGUAGE_CODE, 
                              slug=phrase.slug)
    response = client.get(url)
    assert_html_response(response)


def test_phrase_detail_nonexistent(client):
    """Test the phrase detail view with a non-existent phrase."""
    # Test new slug-based route
    url = build_url_with_query(client, get_phrase_metadata_vw, 
                              target_language_code="el", 
                              slug="nonexistentphrase12345")
    response = client.get(url)
    assert_html_response(response, status_code=404)


def test_sourcefile_views(client):
    """Test sourcefile-related views if any sourcefiles exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir and sourcefile:
        # Test inspect view
        url = build_url_with_query(client, inspect_sourcefile_vw,
                                  target_language_code="el",
                                  sourcedir_slug=sourcedir,
                                  sourcefile_slug=sourcefile)
        response = client.get(url)
        assert_html_response(response)

        # Test text view
        url = build_url_with_query(client, inspect_sourcefile_text_vw,
                                  target_language_code="el",
                                  sourcedir_slug=sourcedir,
                                  sourcefile_slug=sourcefile)
        response = client.get(url)
        assert_html_response(response)

        # Test sentences view
        url = build_url_with_query(client, sourcefile_sentences_vw,
                                  target_language_code="el",
                                  sourcedir_slug=sourcedir,
                                  sourcefile_slug=sourcefile)
        response = client.get(url)
        assert_html_response(response)
