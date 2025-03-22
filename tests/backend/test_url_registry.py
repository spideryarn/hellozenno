"""Tests for the URL registry functionality."""

import pytest
from flask import url_for

from utils.url_registry import endpoint_for
from tests.backend.utils_for_testing import build_url_with_query
from views.lemma_views import get_lemma_metadata_vw
from views.sourcedir_views import sourcefiles_for_sourcedir_vw
from views.sourcedir_api import create_sourcedir_api
from views.core_views import languages_vw
from views.search_views import search_landing_vw


def test_endpoint_for():
    """Test that endpoint_for correctly generates endpoint strings."""
    # Test with get_lemma_metadata_vw (from lemma_views blueprint)
    endpoint = endpoint_for(get_lemma_metadata_vw)
    assert endpoint == "lemma_views.get_lemma_metadata_vw"

    # Test with sourcefiles_for_sourcedir_vw (from sourcedir_views blueprint)
    endpoint = endpoint_for(sourcefiles_for_sourcedir_vw)
    assert endpoint == "sourcedir_views.sourcefiles_for_sourcedir_vw"

    # Test with create_sourcedir_api (from sourcedir_api blueprint)
    endpoint = endpoint_for(create_sourcedir_api)
    assert endpoint == "sourcedir_api.create_sourcedir_api"

    # Test with languages_vw (from core_views blueprint)
    endpoint = endpoint_for(languages_vw)
    assert endpoint == "core_views.languages_vw"

    # Test with search_landing_vw (from search_views blueprint)
    endpoint = endpoint_for(search_landing_vw)
    assert endpoint == "search.search_landing_vw"


def test_build_url_with_query(client):
    """Test the build_url_with_query helper."""
    # Test with route parameters only
    url = build_url_with_query(
        client, get_lemma_metadata_vw, target_language_code="el", lemma="test"
    )

    # The URL should contain the route parameters
    assert "/lang/el/lemma/test" in url

    # Test with query parameters
    url = build_url_with_query(
        client,
        get_lemma_metadata_vw,
        query_params={"tab": "sentences", "page": "2"},
        target_language_code="el",
        lemma="test",
    )

    # The URL should contain both route and query parameters
    assert (
        "/lang/el/lemma/test?tab=sentences&page=2" in url
        or "/lang/el/lemma/test?page=2&tab=sentences" in url
    )
