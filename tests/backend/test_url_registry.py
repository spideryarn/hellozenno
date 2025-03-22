"""Tests for the URL registry functionality."""

import pytest
from flask import url_for

from utils.url_registry import endpoint_for
from tests.backend.utils_for_testing import build_url_with_query, get_route_registry
from views.lemma_views import lemma_detail
from views.sourcedir_views import sourcedirs_list
from views.sourcedir_api import create_sourcedir


def test_endpoint_for():
    """Test that endpoint_for correctly generates endpoint strings."""
    # Test with lemma_detail (from lemma_views blueprint)
    endpoint = endpoint_for(lemma_detail)
    assert endpoint == "lemma.lemma_detail"
    
    # Test with sourcedirs_list (from sourcedir_views blueprint)
    endpoint = endpoint_for(sourcedirs_list)
    assert endpoint == "sourcedir.sourcedirs_list"
    
    # Test with create_sourcedir (from sourcedir_api blueprint)
    endpoint = endpoint_for(create_sourcedir)
    assert endpoint == "sourcedir_api.create_sourcedir"


def test_route_registry_generation(client):
    """Test that the route registry is generated correctly."""
    routes = get_route_registry(client)
    
    # Check that common routes are included
    assert "LEMMA_LEMMA_DETAIL" in routes
    assert "SOURCEDIR_SOURCEDIRS_LIST" in routes
    assert "SOURCEDIR_API_CREATE_SOURCEDIR" in routes
    
    # Check URL template format
    assert "{target_language_code}" in routes["LEMMA_LEMMA_DETAIL"]
    assert "{lemma}" in routes["LEMMA_LEMMA_DETAIL"]


def test_build_url_with_query(client):
    """Test the build_url_with_query helper."""
    # Test with route parameters only
    url = build_url_with_query(
        client,
        lemma_detail,
        target_language_code="el",
        lemma="test"
    )
    
    # The URL should contain the route parameters
    assert "/lang/el/lemma/test" in url
    
    # Test with query parameters
    url = build_url_with_query(
        client,
        lemma_detail,
        query_params={"tab": "sentences", "page": "2"},
        target_language_code="el",
        lemma="test"
    )
    
    # The URL should contain both route and query parameters
    assert "/lang/el/lemma/test?tab=sentences&page=2" in url or \
           "/lang/el/lemma/test?page=2&tab=sentences" in url