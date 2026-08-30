"""Tests for `cache_utils.cache_publicly`, the CDN-caching gate.

The safety argument for marking responses `s-maxage` is entirely in this helper:
cache only when the request is anonymous AND the response is 2xx. Both halves
matter - several read endpoints branch on auth *state*, so caching an anonymous
"log in to generate" body would serve it to logged-in users too. These tests pin
that gate down, since getting it wrong leaks one caller's view to everyone.
"""

import pytest
from flask import Flask, jsonify

from utils.cache_utils import (
    cache_publicly,
    is_anonymous_request,
    S_MAXAGE_DEFAULT,
    STALE_WHILE_REVALIDATE_NONE,
)


@pytest.fixture
def app():
    return Flask(__name__)


def test_anonymous_2xx_is_cacheable(app):
    """The only case that should ever get an s-maxage directive."""
    with app.test_request_context("/api/lang/languages"):
        response = cache_publicly(jsonify({"ok": True}))
        cc = response.headers["Cache-Control"]
        assert f"s-maxage={S_MAXAGE_DEFAULT}" in cc
        assert "public" in cc


def test_authenticated_request_is_never_cached(app):
    """A bearer token means the body may vary by caller, so leave it alone."""
    with app.test_request_context(
        "/api/lang/languages", headers={"Authorization": "Bearer sometoken"}
    ):
        assert not is_anonymous_request()
        response = cache_publicly(jsonify({"ok": True}))
        assert "s-maxage" not in response.headers.get("Cache-Control", "")


@pytest.mark.parametrize("status", [301, 401, 404, 500])
def test_non_2xx_is_never_cached(app, status):
    """Error branches vary by auth state and must not be shared."""
    with app.test_request_context("/api/lang/languages"):
        response = jsonify({"error": "nope"})
        response.status_code = status
        assert "s-maxage" not in cache_publicly(response).headers.get(
            "Cache-Control", ""
        )


def test_stale_while_revalidate_can_be_omitted(app):
    """Passing 0 caps staleness at s_maxage instead of adding a day on top."""
    with app.test_request_context("/api/lang/languages"):
        response = cache_publicly(
            jsonify({"ok": True}),
            s_maxage=60,
            stale_while_revalidate=STALE_WHILE_REVALIDATE_NONE,
        )
        cc = response.headers["Cache-Control"]
        assert "s-maxage=60" in cc
        assert "stale-while-revalidate" not in cc


def test_returns_same_response_object(app):
    """Callers use it inline as `return cache_publicly(jsonify(...))`."""
    with app.test_request_context("/api/lang/languages"):
        response = jsonify({"ok": True})
        assert cache_publicly(response) is response
