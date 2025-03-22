"""Tests for search_views.py functionality."""

import pytest
import urllib.parse
from unittest.mock import patch, MagicMock

from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    TEST_LANGUAGE_NAME,
    create_test_lemma,
    create_test_wordform,
)
from tests.backend.utils_for_testing import assert_html_response, build_url_with_query
from views.search_views import search_landing_vw, search_word_vw


def test_search_landing_page(client):
    """Test the search landing page loads correctly."""
    url = build_url_with_query(
        client, 
        search_landing_vw, 
        target_language_code=TEST_LANGUAGE_CODE
    )
    response = client.get(url)
    assert_html_response(response)
    assert "Search" in response.data.decode()
    assert TEST_LANGUAGE_NAME in response.data.decode()


def test_search_landing_with_query_redirects(client):
    """Test that search landing with query redirects to search_word."""
    url = build_url_with_query(
        client,
        search_landing_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        query_params={"q": "test"}
    )
    response = client.get(url)
    assert response.status_code == 302
    assert f"/lang/{TEST_LANGUAGE_CODE}/search/test" in response.headers.get("Location")


def test_search_word_redirects_to_wordform(client, fixture_for_testing_db):
    """Test search_word redirects to get_wordform_metadata."""
    # Create a test wordform
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)
    
    # Test the search redirect
    url = build_url_with_query(
        client,
        search_word_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform=wordform.wordform
    )
    response = client.get(url)
    assert response.status_code == 302
    assert f"/lang/{TEST_LANGUAGE_CODE}/wordform/{wordform.wordform}" in response.headers.get("Location")


# Mock for the enhanced search response format
def mock_enhanced_search_for_wordform(wordform, target_language_code, verbose=1):
    """Mock for the enhanced quick_search_for_wordform function that returns both target language and English results."""
    if wordform == "example":
        # English word search
        return {
            "target_language_results": {
                "matches": [],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [
                    {
                        "target_language_wordform": "παράδειγμα",
                        "target_language_lemma": "παράδειγμα",
                        "part_of_speech": "noun",
                        "english": ["example", "model", "paradigm"],
                        "inflection_type": "neuter singular nominative/accusative"
                    }
                ],
                "possible_misspellings": None
            }
        }, {}
    elif wordform == "both":
        # Word valid in both languages
        return {
            "target_language_results": {
                "matches": [
                    {
                        "target_language_wordform": "both",
                        "target_language_lemma": "both",
                        "part_of_speech": "adverb",
                        "english": ["και οι δύο"],
                        "inflection_type": "adverb"
                    }
                ],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [
                    {
                        "target_language_wordform": "και οι δύο",
                        "target_language_lemma": "και οι δύο",
                        "part_of_speech": "phrase",
                        "english": ["both"],
                        "inflection_type": "phrase"
                    }
                ],
                "possible_misspellings": None
            }
        }, {}
    elif wordform == "nonexistent":
        # No matches
        return {
            "target_language_results": {
                "matches": [],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}
    elif wordform == "misspelled":
        # Typo case
        return {
            "target_language_results": {
                "matches": [],
                "possible_misspellings": ["correct"]
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}
    elif wordform == "single_match":
        # Single match case - should redirect directly
        return {
            "target_language_results": {
                "matches": [
                    {
                        "target_language_wordform": "μοναδικό",
                        "target_language_lemma": "μοναδικός",
                        "part_of_speech": "adjective",
                        "english": ["unique", "single"],
                        "inflection_type": "neuter singular nominative/accusative"
                    }
                ],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}
    else:
        # Default - just target language match
        return {
            "target_language_results": {
                "matches": [
                    {
                        "target_language_wordform": wordform,
                        "target_language_lemma": wordform,
                        "part_of_speech": "noun",
                        "english": ["test translation"],
                        "inflection_type": "nominative"
                    }
                ],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}


@patch("views.wordform_views.quick_search_for_wordform", side_effect=mock_enhanced_search_for_wordform)
def test_enhanced_search_english_word(mock_search, client):
    """Test searching for an English word redirects to the translation results."""
    from views.wordform_views import get_wordform_metadata_vw
    
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="example"
    )
    response = client.get(url)
    assert response.status_code == 302
    location = response.headers.get("Location")
    # The URL will be URL-encoded for Greek characters
    assert "/wordform/" in location
    assert "παράδειγμα" in urllib.parse.unquote(location)


@patch("views.wordform_views.quick_search_for_wordform", side_effect=mock_enhanced_search_for_wordform)
def test_enhanced_search_single_match(mock_search, client):
    """Test search with a single match redirects to the wordform."""
    from views.wordform_views import get_wordform_metadata_vw
    
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="single_match"
    )
    response = client.get(url)
    assert response.status_code == 302
    location = response.headers.get("Location")
    # The URL will be URL-encoded for Greek characters
    assert "/wordform/" in location
    assert "μοναδικό" in urllib.parse.unquote(location)


@patch("views.wordform_views.quick_search_for_wordform", side_effect=mock_enhanced_search_for_wordform)
def test_enhanced_search_both_languages(mock_search, client):
    """Test search for a word valid in both languages."""
    from views.wordform_views import get_wordform_metadata_vw
    
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="both"
    )
    response = client.get(url)
    assert_html_response(response)
    
    # Should display results from both sections
    data = response.data.decode()
    assert "Search Results for" in data
    assert "both" in data
    assert "και οι δύο" in data


@patch("views.wordform_views.quick_search_for_wordform", side_effect=mock_enhanced_search_for_wordform)
def test_enhanced_search_no_matches(mock_search, client):
    """Test search with no matches."""
    from views.wordform_views import get_wordform_metadata_vw
    
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="nonexistent"
    )
    response = client.get(url)
    assert_html_response(response)
    
    # Should display invalid word template
    data = response.data.decode()
    assert "Invalid Word" in data
    assert "nonexistent" in data


@patch("views.wordform_views.quick_search_for_wordform", side_effect=mock_enhanced_search_for_wordform)
def test_enhanced_search_misspelled(mock_search, client):
    """Test search with possible misspellings."""
    from views.wordform_views import get_wordform_metadata_vw
    
    url = build_url_with_query(
        client,
        get_wordform_metadata_vw,
        target_language_code=TEST_LANGUAGE_CODE,
        wordform="misspelled"
    )
    response = client.get(url)
    assert_html_response(response)
    
    # Should display translation search results with suggestions
    data = response.data.decode()
    assert "Search Results for" in data or "Invalid Word" in data  # Either template is acceptable
    assert "misspelled" in data
    assert "correct" in data  # The suggested correction should be displayed