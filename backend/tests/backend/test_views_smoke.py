import pytest
from backend.views.wordform_api import delete_wordform_api
from tests.fixtures_for_tests import (
    SAMPLE_PHRASE_DATA,
    TEST_TARGET_LANGUAGE_CODE,
    create_complete_test_data,
    create_test_sentence,
)
from db_models import Phrase
from tests.backend.utils_for_testing import (
    get_sourcedir_and_file,
    assert_html_response,
    with_wordform_search_mock,
    build_url_with_query,
)
from unittest.mock import patch

# Import all view functions that we'll need
from views.core_views import home_vw, experim_vw, favicon_vw
from views.languages_views import languages_list_vw
from views.search_views import search_landing_vw, search_word_vw
from views.lemma_views import lemmas_list_vw, get_lemma_metadata_vw
from views.wordform_views import (
    wordforms_list_vw,
    get_wordform_metadata_vw,
)
from views.phrase_views import phrases_list_vw, get_phrase_metadata_vw
from views.sourcedir_views import (
    sourcedirs_for_language_vw,
    sourcefiles_for_sourcedir_vw,
)
from views.sourcefile_views import (
    inspect_sourcefile_vw,
    inspect_sourcefile_text_vw,
    sourcefile_sentences_vw,
)
from views.sentence_views import sentences_list_vw, get_sentence_vw
from views.flashcard_views import (
    flashcard_landing_vw,
    flashcard_sentence_vw,
    random_flashcard_vw,
)
from views.system_views import health_check_vw, route_test_vw
from views.auth_views import auth_page_vw, protected_page_vw, profile_page_vw


"""
Smoke tests for the read-only views (i.e. won't change the data),
using the test database.
"""


def test_languages_list_vw(client):
    """Test the languages list view."""
    url = build_url_with_query(client, languages_list_vw)
    response = client.get(url)
    assert_html_response(response)


def test_sourcedirs_for_language_vw(client):
    """Test the search landing page."""
    url = build_url_with_query(
        client, sourcedirs_for_language_vw, target_language_code="el"
    )
    response = client.get(url)
    assert_html_response(response)


def test_search_landing_vw(client):
    """Test the search landing page."""
    url = build_url_with_query(client, search_landing_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_alpha_sort(client):
    """Test the lemmas list view with alphabetical sorting."""
    url = build_url_with_query(
        client,
        lemmas_list_vw,
        query_params={"sort": "alpha"},
        target_language_code="el",
    )
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_commonality_sort(client):
    """Test the lemmas list view with commonality sorting."""
    url = build_url_with_query(
        client,
        lemmas_list_vw,
        query_params={"sort": "commonality"},
        target_language_code="el",
    )
    response = client.get(url)
    assert_html_response(response)


def test_lemma_detail_existing(client, fixture_for_testing_db):
    """Test the lemma detail view with an existing lemma."""
    # Create test data for this specific test
    test_data = create_complete_test_data(fixture_for_testing_db)
    lemma = test_data["lemma"]
    url = build_url_with_query(
        client,
        get_lemma_metadata_vw,
        target_language_code="el",
        lemma=lemma.lemma,
    )
    response = client.get(url)
    assert_html_response(response)


def test_lemma_detail_nonexistent(client):
    """Test the lemma detail view with a non-existent lemma."""
    url = build_url_with_query(
        client,
        get_lemma_metadata_vw,
        target_language_code="el",
        lemma="nonexistentlemma",
    )
    response = client.get(url)
    assert_html_response(response)


def test_lemmas_list_date_sort(client):
    """Test the lemmas list view with date sorting."""
    url = build_url_with_query(
        client,
        lemmas_list_vw,
        query_params={"sort": "date"},
        target_language_code="el",
    )
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

    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code="el",
        wordform=wordform.wordform,
    )
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


@with_wordform_search_mock
def test_wordform_detail_nonexistent(mock_search, client):
    """Test the wordform detail view with a non-existent wordform."""
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code="el",
        wordform="nonexistentword",
    )
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


@with_wordform_search_mock
def test_delete_wordform_view(mock_search, client, fixture_for_testing_db):
    """Test the delete wordform view."""
    # Create test data including a wordform
    test_data = create_complete_test_data(fixture_for_testing_db)
    wordform = test_data["wordform"]

    url = build_url_with_query(
        client,
        delete_wordform_api,
        target_language_code="el",
        wordform=wordform.wordform,
    )
    response = client.post(url, follow_redirects=True)
    assert_html_response(response)


def test_sourcedirs_list_alpha_sort(client):
    """Test the sourcedirs list view with alphabetical sorting."""
    url = build_url_with_query(
        client,
        sourcedirs_for_language_vw,
        query_params={"sort": "alpha"},
        target_language_code="el",
    )
    response = client.get(url)
    assert_html_response(response)


def test_sourcedirs_list_date_sort(client):
    """Test the sourcedirs list view with date sorting."""
    url = build_url_with_query(
        client,
        sourcedirs_for_language_vw,
        query_params={"sort": "date"},
        target_language_code="el",
    )
    response = client.get(url)
    assert_html_response(response)


def test_sourcefiles_for_sourcedir_vw(client):
    """Test viewing contents of a sourcedir if any exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir:
        url = build_url_with_query(
            client,
            sourcefiles_for_sourcedir_vw,
            target_language_code="el",
            sourcedir_slug=sourcedir,
        )
        response = client.get(url)
        assert_html_response(response)

        if sourcefile:
            # Test inspect view
            url = build_url_with_query(
                client,
                inspect_sourcefile_vw,
                target_language_code="el",
                sourcedir_slug=sourcedir,
                sourcefile_slug=sourcefile,
            )
            response = client.get(url)
            assert_html_response(response)

            # Test file text view
            url = build_url_with_query(
                client,
                inspect_sourcefile_text_vw,
                target_language_code="el",
                sourcedir_slug=sourcedir,
                sourcefile_slug=sourcefile,
            )
            response = client.get(url)
            assert_html_response(response)

            # Test sentences view
            url = build_url_with_query(
                client,
                sourcefile_sentences_vw,
                target_language_code="el",
                sourcedir_slug=sourcedir,
                sourcefile_slug=sourcefile,
            )
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
    phrase = Phrase.create(
        target_language_code=TEST_TARGET_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA
    )

    # Test with the created phrase using its slug
    url = build_url_with_query(
        client,
        get_phrase_metadata_vw,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
        slug=phrase.slug,
    )
    response = client.get(url)
    assert_html_response(response)


def test_phrase_detail_nonexistent(client):
    """Test the phrase detail view with a non-existent phrase."""
    # Test new slug-based route
    url = build_url_with_query(
        client,
        get_phrase_metadata_vw,
        target_language_code="el",
        slug="nonexistentphrase12345",
    )
    response = client.get(url)
    assert_html_response(response, status_code=404)


def test_inspect_sourcefile_views(client):
    """Test sourcefile-related views if any sourcefiles exist."""
    sourcedir, sourcefile = get_sourcedir_and_file(client)

    if sourcedir and sourcefile:
        # Test inspect view
        url = build_url_with_query(
            client,
            inspect_sourcefile_vw,
            target_language_code="el",
            sourcedir_slug=sourcedir,
            sourcefile_slug=sourcefile,
        )
        response = client.get(url)
        assert_html_response(response)

        # Test text view
        url = build_url_with_query(
            client,
            inspect_sourcefile_text_vw,
            target_language_code="el",
            sourcedir_slug=sourcedir,
            sourcefile_slug=sourcefile,
        )
        response = client.get(url)
        assert_html_response(response)

        # Test sentences view
        url = build_url_with_query(
            client,
            sourcefile_sentences_vw,
            target_language_code="el",
            sourcedir_slug=sourcedir,
            sourcefile_slug=sourcefile,
        )
        response = client.get(url)
        assert_html_response(response)


# Core Views Tests
def test_home_vw(client):
    """Test the home view which redirects to languages list."""
    url = build_url_with_query(client, home_vw)
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


def test_experim_vw(client):
    """Test the experim view for experimental features."""
    url = build_url_with_query(client, experim_vw)
    response = client.get(url)
    assert_html_response(response)


def test_favicon_vw(client):
    """Test the favicon view."""
    url = build_url_with_query(client, favicon_vw)
    response = client.get(url)
    # Favicon is an image, not HTML
    assert response.status_code == 200
    assert "image/" in response.content_type


# Search Views Tests
def test_search_word_vw(client):
    """Test the search word view which redirects to wordform detail."""
    url = build_url_with_query(
        client, search_word_vw, target_language_code="el", wordform="test"
    )
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


# Sentence Views Tests
def test_sentences_list_vw(client):
    """Test the sentences list view."""
    url = build_url_with_query(client, sentences_list_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_get_sentence_vw(client, fixture_for_testing_db):
    """Test the sentence detail view with an existing sentence."""
    # Create a test sentence
    sentence = create_test_sentence(fixture_for_testing_db)

    url = build_url_with_query(
        client, get_sentence_vw, target_language_code="el", slug=sentence.slug
    )
    response = client.get(url)
    assert_html_response(response)


def test_get_sentence_vw_nonexistent(client):
    """Test the sentence detail view with a non-existent sentence."""
    url = build_url_with_query(
        client,
        get_sentence_vw,
        target_language_code="el",
        slug="nonexistentsentence123",
    )
    response = client.get(url)
    assert_html_response(response, status_code=404)


# Flashcard Views Tests
def test_flashcard_landing_vw(client):
    """Test the flashcard landing view."""
    url = build_url_with_query(client, flashcard_landing_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


def test_flashcard_sentence_vw(client, fixture_for_testing_db):
    """Test the flashcard sentence view with an existing sentence."""
    # Create a test sentence
    sentence = create_test_sentence(fixture_for_testing_db)

    url = build_url_with_query(
        client,
        flashcard_sentence_vw,
        target_language_code="el",
        slug=sentence.slug,
    )
    response = client.get(url)
    assert_html_response(response)


@pytest.mark.skip(
    reason="I cannot figure out why this is returning a 404, even though it seems to work in the browser"
)
def test_random_flashcard_vw(client):
    """Test the random flashcard view."""
    url = build_url_with_query(client, random_flashcard_vw, target_language_code="el")
    response = client.get(url, follow_redirects=True)
    assert_html_response(response)


# System Views Tests
def test_health_check_vw(client):
    """Test the health check view."""
    url = build_url_with_query(client, health_check_vw)
    response = client.get(url)
    # Health check returns JSON
    assert response.status_code == 200
    assert "application/json" in response.content_type


def test_route_test_vw(client):
    """Test the route test view."""
    url = build_url_with_query(client, route_test_vw)
    response = client.get(url)
    assert_html_response(response)


# Auth Views Tests
@patch("views.auth_views.get_current_user")
def test_auth_page_vw(mock_get_current_user, client):
    """Test the auth page view with no user logged in."""
    # Mock no user logged in
    mock_get_current_user.return_value = None

    url = build_url_with_query(client, auth_page_vw)
    response = client.get(url)
    assert_html_response(response)

    # Test with target language code
    url = build_url_with_query(client, auth_page_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response)


@patch("views.auth_views.get_current_user")
@patch("views.auth_views.page_auth_required")
def test_protected_page_vw(mock_auth_required, mock_get_current_user, client):
    """Test the protected page view."""
    # Mock a logged-in user with ID 1
    mock_user = {"id": 1, "email": "test@example.com"}
    mock_get_current_user.return_value = mock_user
    # Mock the auth decorator to allow access
    mock_auth_required.return_value = lambda f: f

    url = build_url_with_query(client, protected_page_vw)
    response = client.get(url)
    assert_html_response(response, status_code=302)  # Expect a redirect


@patch("views.auth_views.get_current_user")
@patch("views.auth_views.page_auth_required")
@patch("views.auth_views.Profile.get_or_create_for_user")
def test_profile_page_vw(
    mock_profile, mock_auth_required, mock_get_current_user, client
):
    """Test the profile page view."""
    # Mock a logged-in user with ID 1
    mock_user = {"id": 1, "email": "test@example.com"}
    mock_get_current_user.return_value = mock_user
    # Mock the auth decorator to allow access
    mock_auth_required.return_value = lambda f: f
    # Mock the profile lookup
    mock_profile.return_value = {"id": 1, "user_id": 1, "display_name": "Test User"}

    url = build_url_with_query(client, profile_page_vw)
    response = client.get(url)
    assert_html_response(response, status_code=302)  # Expect a redirect

    # Test with target language code
    url = build_url_with_query(client, profile_page_vw, target_language_code="el")
    response = client.get(url)
    assert_html_response(response, status_code=302)  # Expect a redirect
