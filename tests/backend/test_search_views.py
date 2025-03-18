"""Tests for search_views.py functionality."""

import pytest
from unittest.mock import patch, MagicMock

from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    TEST_LANGUAGE_NAME,
    create_test_lemma,
    create_test_wordform,
)
from tests.backend.utils_for_testing import assert_html_response


def test_search_landing_page(client):
    """Test the search landing page loads correctly."""
    response = client.get(f"/lang/{TEST_LANGUAGE_CODE}/search")
    assert_html_response(response)
    assert "Search" in response.data.decode()
    assert TEST_LANGUAGE_NAME in response.data.decode()


def test_search_landing_with_query_redirects(client):
    """Test that search landing with query redirects to search_word."""
    response = client.get(f"/lang/{TEST_LANGUAGE_CODE}/search?q=test")
    assert response.status_code == 302
    assert f"/lang/{TEST_LANGUAGE_CODE}/search/test" in response.headers.get("Location")


def test_search_word_redirects_to_wordform(client, fixture_for_testing_db):
    """Test search_word redirects to get_wordform_metadata."""
    # Create a test wordform
    lemma = create_test_lemma(fixture_for_testing_db)
    wordform = create_test_wordform(fixture_for_testing_db, lemma)
    
    # Test the search redirect
    response = client.get(f"/lang/{TEST_LANGUAGE_CODE}/search/{wordform.wordform}")
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
                        "wordform": "παράδειγμα",
                        "lemma": "παράδειγμα",
                        "part_of_speech": "noun",
                        "translations": ["example", "model", "paradigm"],
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
                        "wordform": "both",
                        "lemma": "both",
                        "part_of_speech": "adverb",
                        "translations": ["και οι δύο"],
                        "inflection_type": "adverb"
                    }
                ],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [
                    {
                        "wordform": "και οι δύο",
                        "lemma": "και οι δύο",
                        "part_of_speech": "phrase",
                        "translations": ["both"],
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
    else:
        # Default - just target language match
        return {
            "target_language_results": {
                "matches": [
                    {
                        "wordform": wordform,
                        "lemma": wordform,
                        "part_of_speech": "noun",
                        "translations": ["test translation"],
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