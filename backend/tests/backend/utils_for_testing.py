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
    TEST_TARGET_LANGUAGE_CODE,
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
    client, target_language_code: str = "el"
) -> Tuple[Optional[str], Optional[str]]:
    """Get a sourcedir and sourcefile for testing.

    Args:
        client: The Flask test client
        target_language_code: The language code to use

    Returns:
        A tuple of (sourcedir, sourcefile) or (None, None) if not found
    """
    from views.sourcedir_views import (
        sourcedirs_for_language_vw,
        sourcefiles_for_sourcedir_vw,
    )

    # Get the list of sourcedirs
    url = build_url_with_query(
        client,
        sourcedirs_for_language_vw,
        target_language_code=target_language_code,
    )
    response = client.get(url)
    if response.status_code != 200:
        return None, None

    html = response.data.decode()
    sourcedir = extract_data_attribute(html, "sourcedir")
    if not sourcedir:
        return None, None

    # Get sourcedir contents
    url = build_url_with_query(
        client,
        sourcefiles_for_sourcedir_vw,
        target_language_code=target_language_code,
        sourcedir_slug=sourcedir,
    )
    response = client.get(url)
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
        "utils.vocab_llm_utils.quick_search_for_wordform",
        side_effect=mock_quick_search_for_wordform,
    )(func)


# Function removed: create_test_entity
# Use the specific create_test_* functions from tests.fixtures_for_tests directly instead


def build_url_with_query(client, view_func, query_params=None, **url_params):
    """
    Build a complete URL with route and query parameters for testing.

    This helper makes it easier to build URLs for testing views by handling both
    route parameters and query parameters.

    Args:
        client: The Flask test client
        view_func: The view function
        query_params: Optional dict of query parameters
        **url_params: Route parameters as keyword arguments
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
