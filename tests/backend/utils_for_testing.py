"""Common utilities for backend tests."""

import re
from urllib.parse import quote, urlencode
from typing import Tuple, Optional, Callable, Dict, Any, Union
from unittest.mock import patch
from functools import wraps
from flask import url_for

from utils.url_registry import endpoint_for, generate_route_registry

from tests.mocks import mock_quick_search_for_wordform
from tests.fixtures_for_tests import (
    TEST_LANGUAGE_CODE,
    SAMPLE_LEMMA_DATA,
    SAMPLE_PHRASE_DATA,
)
from db_models import (
    Lemma,
    Wordform,
    Phrase,
    Sourcedir,
    Sourcefile,
)


def extract_data_attribute(html: str, attribute_name: str) -> Optional[str]:
    """Extract a data attribute value from HTML.

    Args:
        html: The HTML string to search
        attribute_name: The name of the data attribute (without 'data-' prefix)

    Returns:
        The value of the data attribute, or None if not found
    """
    pattern = f'data-{attribute_name}="([^"]*)"'
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return None


def get_sourcedir_and_file(
    client, language_code: str = "el"
) -> Tuple[Optional[str], Optional[str]]:
    """Get a sourcedir and sourcefile for testing.

    Args:
        client: The Flask test client
        language_code: The language code to use

    Returns:
        A tuple of (sourcedir, sourcefile) or (None, None) if not found
    """
    # Get the list of sourcedirs
    response = client.get(f"/{language_code}/")
    if response.status_code != 200:
        return None, None

    html = response.data.decode()
    sourcedir = extract_data_attribute(html, "sourcedir")
    if not sourcedir:
        return None, None

    # Get sourcedir contents
    response = client.get(f"/{language_code}/{quote(sourcedir)}")
    if response.status_code != 200:
        return sourcedir, None

    html = response.data.decode()
    sourcefile = extract_data_attribute(html, "sourcefile")

    return sourcedir, sourcefile


def assert_html_response(response, status_code=200):
    """Assert that a response is a valid HTML response with the expected status code.

    Args:
        response: The Flask response object
        status_code: The expected status code (default: 200)
    """
    assert response.status_code == status_code
    if status_code == 200:
        assert "text/html" in response.content_type


def with_wordform_search_mock(func: Callable) -> Callable:
    """Decorator to patch the quick_search_for_wordform function.

    This decorator should be used on test functions that need to mock the
    quick_search_for_wordform function. The test function should accept
    a mock_search parameter as its first parameter.

    Example:
        @with_wordform_search_mock
        def test_function(mock_search, client):
            # Test code here

    Args:
        func: The test function to decorate

    Returns:
        The decorated function
    """
    return patch(
        "views.wordform_views.quick_search_for_wordform",
        side_effect=mock_quick_search_for_wordform,
    )(func)


def create_test_entity(db, entity_type: str, **kwargs) -> Any:
    """Create a test entity with the given parameters.

    Args:
        db: The database connection
        entity_type: The type of entity to create ('lemma', 'wordform', 'phrase', 'sourcedir', 'sourcefile')
        **kwargs: Additional parameters to pass to the entity creation function

    Returns:
        The created entity
    """
    if entity_type == "lemma":
        # Use sample data as defaults, but allow overrides
        lemma_data = {**SAMPLE_LEMMA_DATA}
        lemma_data.update(kwargs)

        # Ensure required fields are present
        if "lemma" not in lemma_data:
            lemma_data["lemma"] = "test_lemma"
        if "language_code" not in lemma_data:
            lemma_data["language_code"] = TEST_LANGUAGE_CODE

        return Lemma.create(**lemma_data)

    elif entity_type == "wordform":
        # Ensure we have a lemma
        lemma = kwargs.pop("lemma", None)
        if not lemma:
            lemma = create_test_entity(db, "lemma")

        # Set defaults
        wordform_data = {
            "wordform": kwargs.pop("wordform", "test_wordform"),
            "lemma_entry": lemma,
            "language_code": kwargs.pop("language_code", TEST_LANGUAGE_CODE),
            "part_of_speech": kwargs.pop("part_of_speech", "noun"),
            "translations": kwargs.pop("translations", ["test translation"]),
            "inflection_type": kwargs.pop("inflection_type", "nominative"),
            "is_lemma": kwargs.pop("is_lemma", True),
        }

        # Add any remaining kwargs
        wordform_data.update(kwargs)

        return Wordform.create(**wordform_data)

    elif entity_type == "phrase":
        # Use sample data as defaults, but allow overrides
        phrase_data = {**SAMPLE_PHRASE_DATA}
        phrase_data.update(kwargs)

        # Ensure language_code is present
        if "language_code" not in phrase_data:
            phrase_data["language_code"] = TEST_LANGUAGE_CODE

        return Phrase.create(**phrase_data)

    elif entity_type == "sourcedir":
        sourcedir_data = {
            "path": kwargs.pop("path", "test_dir"),
            "language_code": kwargs.pop("language_code", TEST_LANGUAGE_CODE),
        }

        # Add any remaining kwargs
        sourcedir_data.update(kwargs)

        return Sourcedir.create(**sourcedir_data)

    elif entity_type == "sourcefile":
        # Ensure we have a sourcedir
        sourcedir = kwargs.pop("sourcedir", None)
        if not sourcedir:
            sourcedir = create_test_entity(db, "sourcedir")

        # Set defaults
        sourcefile_data = {
            "sourcedir": sourcedir,
            "filename": kwargs.pop("filename", "test.txt"),
            "text_target": kwargs.pop("text_target", "test text"),
            "text_english": kwargs.pop("text_english", "test translation"),
            "description": kwargs.pop("description", "Test file description"),
            "metadata": kwargs.pop(
                "metadata",
                {
                    "words": [
                        {
                            "wordform": "test",
                            "lemma": "test",
                            "part_of_speech": "noun",
                            "translations": ["test translation"],
                        }
                    ],
                    "phrases": [
                        {
                            "canonical_form": "test phrase",
                            "raw_forms": ["test phrase"],
                            "translations": ["test translation"],
                            "part_of_speech": "verbal phrase",
                            "centrality": 0.8,
                            "ordering": 1,
                        }
                    ],
                },
            ),
            "image_data": kwargs.pop("image_data", b"test content"),
            "audio_data": kwargs.pop("audio_data", b"test audio content"),
            "sourcefile_type": kwargs.pop("sourcefile_type", "image"),
        }

        # Add any remaining kwargs
        sourcefile_data.update(kwargs)

        return Sourcefile.create(**sourcefile_data)

    else:
        raise ValueError(f"Unknown entity type: {entity_type}")


def build_url_with_query(client, view_func, query_params=None, **url_params):
    """Build a URL with query parameters for testing.
    
    This is a test-specific helper that safely builds URLs with both
    route parameters and query parameters.
    
    Args:
        client: The Flask test client
        view_func: The view function to build the URL for
        query_params: A dictionary of query parameters
        **url_params: Parameters for url_for()
        
    Returns:
        str: The full URL
    """
    # Using client.application.test_request_context for Flask context
    with client.application.test_request_context():
        # Get the correct endpoint string using our helper
        endpoint_string = endpoint_for(view_func)
        base_url = url_for(endpoint_string, **url_params)
        
    if query_params:
        query_string = urlencode(query_params)
        return f"{base_url}?{query_string}"
    
    return base_url


def get_route_registry(client):
    """Get the route registry for testing.
    
    This allows tests to use the route registry for URL resolution.
    
    Args:
        client: The Flask test client
        
    Returns:
        dict: The route registry
    """
    with client.application.app_context():
        return generate_route_registry(client.application)
