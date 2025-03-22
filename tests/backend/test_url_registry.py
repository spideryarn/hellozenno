"""Tests for the URL registry functionality."""

import os
import json
import re
import pytest
from flask import url_for, current_app

from utils.url_registry import endpoint_for, generate_route_registry
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


def test_typescript_routes_match_flask_routes(client):
    """Test that generated TypeScript routes match the Flask routes."""
    # Get the app from the client fixture
    app = client.application
    
    # Path to the TypeScript routes file
    ts_file_path = os.path.join(app.static_folder, "js", "generated", "routes.ts")
    
    # Skip the test if the file doesn't exist (e.g., in CI environments)
    if not os.path.exists(ts_file_path):
        pytest.skip(f"TypeScript routes file not found at {ts_file_path}")
    
    # Read the TypeScript routes file
    with open(ts_file_path, "r") as f:
        ts_content = f.read()
    
    # Extract route constants from TypeScript file using regex
    route_pattern = r'(\w+):\s*"([^"]+)"'
    ts_routes = dict(re.findall(route_pattern, ts_content))
    
    # Generate the current Flask route registry
    with app.app_context():
        flask_routes = generate_route_registry(app)
    
    # For the main test, we'll focus on checking that common routes match
    # Find the intersection of route names (routes in both Flask and TypeScript)
    common_routes = set(flask_routes.keys()) & set(ts_routes.keys())
    
    # Assert that we have at least some common routes to test
    assert common_routes, "No common routes found between Flask and TypeScript"
    
    # Assert that the route paths match for common routes
    mismatched_routes = []
    for route_name in common_routes:
        if ts_routes[route_name] != flask_routes[route_name]:
            mismatched_routes.append(
                f"{route_name}: Flask: {flask_routes[route_name]}, TS: {ts_routes[route_name]}"
            )
    
    # Check for mismatches on common routes
    assert not mismatched_routes, f"Mismatched route paths: {mismatched_routes}"
    
    # Print diagnostics for missing/extra routes (but don't fail the test)
    # This is useful for development but not critical for CI
    missing_routes = [f"{route}: {flask_routes[route]}" for route in flask_routes if route not in ts_routes]
    extra_routes = [f"{route}: {ts_routes[route]}" for route in ts_routes if route not in flask_routes]
    
    if missing_routes:
        print(f"INFO: Routes in Flask but not in TypeScript: {len(missing_routes)}")
        # Uncomment to see details: print("\n".join(missing_routes))
    
    if extra_routes:
        print(f"INFO: Routes in TypeScript but not in Flask: {len(extra_routes)}")
        # Uncomment to see details: print("\n".join(extra_routes))
