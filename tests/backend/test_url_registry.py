"""Tests for the URL registry functionality."""

import pytest
from flask import url_for

from utils.url_registry import endpoint_for
from tests.backend.utils_for_testing import build_url_with_query, get_route_registry
from views.lemma_views import get_lemma_metadata
from views.sourcedir_views import sourcefiles_for_sourcedir
from views.sourcedir_api import create_sourcedir_api


def test_endpoint_for():
    """Test that endpoint_for correctly generates endpoint strings."""
    # Test with get_lemma_metadata (from lemma_views blueprint)
    endpoint = endpoint_for(get_lemma_metadata)
    assert endpoint == "lemma_views.get_lemma_metadata"
    
    # Test with sourcefiles_for_sourcedir (from sourcedir_views blueprint)
    endpoint = endpoint_for(sourcefiles_for_sourcedir)
    assert endpoint == "sourcedir_views.sourcefiles_for_sourcedir"
    
    # Test with create_sourcedir_api (from sourcedir_api blueprint)
    endpoint = endpoint_for(create_sourcedir_api)
    assert endpoint == "sourcedir_api.create_sourcedir_api"


def test_route_registry_generation(client):
    """Test that the route registry is generated correctly."""
    routes = get_route_registry(client)
    
    # Check that common routes are included
    assert "LEMMA_VIEWS_GET_LEMMA_METADATA" in routes
    assert "SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR" in routes
    assert "SOURCEDIR_API_CREATE_SOURCEDIR_API" in routes
    
    # Check URL template format
    assert "{target_language_code}" in routes["LEMMA_VIEWS_GET_LEMMA_METADATA"]
    assert "{lemma}" in routes["LEMMA_VIEWS_GET_LEMMA_METADATA"]


def test_build_url_with_query(client):
    """Test the build_url_with_query helper."""
    # Test with route parameters only
    url = build_url_with_query(
        client,
        get_lemma_metadata,
        target_language_code="el",
        lemma="test"
    )
    
    # The URL should contain the route parameters
    assert "/lang/el/lemma/test" in url
    
    # Test with query parameters
    url = build_url_with_query(
        client,
        get_lemma_metadata,
        query_params={"tab": "sentences", "page": "2"},
        target_language_code="el",
        lemma="test"
    )
    
    # The URL should contain both route and query parameters
    assert "/lang/el/lemma/test?tab=sentences&page=2" in url or \
           "/lang/el/lemma/test?page=2&tab=sentences" in url