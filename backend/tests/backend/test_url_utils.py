"""
Tests for URL utilities including encoding/decoding functions.

see planning/250316_vercel_url_encoding_fix.md
"""

import pytest
from unittest.mock import patch, MagicMock
import urllib.parse
from flask import g, request, Flask

from utils.url_utils import fix_url_encoding, decode_url_params


# Unit tests for fix_url_encoding function
def test_fix_url_encoding_with_normal_url():
    """Test fix_url_encoding with a normal URL without encoding."""
    test_url = "/el/wordform/test"
    result = fix_url_encoding(test_url)
    assert result == test_url


def test_fix_url_encoding_with_single_encoded_url():
    """Test fix_url_encoding with a URL containing percent-encoded sequences."""
    # Greek word "δοκιμή" (test) encoded
    test_url = "/el/wordform/%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE"
    expected = "/el/wordform/δοκιμή"
    result = fix_url_encoding(test_url)
    assert result == expected


def test_fix_url_encoding_with_double_encoded_url():
    """Test fix_url_encoding with a double-encoded URL."""
    # Greek word "δοκιμή" double-encoded
    test_url = (
        "/el/wordform/%25CE%25B4%25CE%25BF%25CE%25BA%25CE%25B9%25CE%25BC%25CE%25AE"
    )
    expected = "/el/wordform/%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE"
    result = fix_url_encoding(test_url)
    assert result == expected


def test_fix_url_encoding_with_mixed_characters():
    """Test fix_url_encoding with a URL containing both encoded and non-encoded chars."""
    test_url = "/el/wordform/test-%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE"
    expected = "/el/wordform/test-δοκιμή"
    result = fix_url_encoding(test_url)
    assert result == expected


def test_fix_url_encoding_with_invalid_encoding():
    """Test fix_url_encoding with invalid UTF-8 encoding."""
    # Invalid UTF-8 sequence
    test_url = "/el/wordform/%FF%FE"
    result = fix_url_encoding(test_url)
    # Should return something, even if it's a replacement character
    assert result is not None


# Flask app fixture for middleware tests
@pytest.fixture
def app():
    """Create a test Flask app."""
    app = Flask(__name__)
    app.testing = True
    return app


# Tests for decode_url_params middleware
def test_decode_url_params_with_encoded_url(app):
    """Test the decode_url_params middleware with an encoded URL."""
    with app.test_request_context("/el/wordform/%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE"):
        # The Flask test_request_context has automatically decoded the URL
        # Use the request.path directly without patching fix_url_encoding
        # Verify that decode_url_params works correctly

        # Store the original path before our function changes it
        original_path = request.path

        # Call the function without mocking
        decode_url_params()

        # In this case, nothing should change since Flask already decoded it
        assert g.original_url == original_path
        assert request.path == original_path


def test_decode_url_params_simulated_vercel(app):
    """Simulate Vercel environment with double-encoded URL."""
    # This test simulates what happens in Vercel
    # by patching request.path to contain the encoded value
    with app.test_request_context("/el/wordform/test"):
        # Simulate double-encoding like Vercel might have
        double_encoded = (
            "/el/wordform/%25CE%25B4%25CE%25BF%25CE%25BA%25CE%25B9%25CE%25BC%25CE%25AE"
        )

        # Patch request.path to have the double-encoded value
        with patch.object(request, "path", double_encoded):
            # Call the function
            decode_url_params()

            # Verify it was fixed properly
            assert g.original_url == double_encoded
            # Check that path was updated
            assert request.path != double_encoded
            assert "%CE%B4%CE%BF%CE%BA%CE%B9%CE%BC%CE%AE" in request.path


def test_decode_url_params_with_normal_url(app):
    """Test the decode_url_params middleware with a normal URL (no encoding)."""
    with app.test_request_context("/el/wordform/test"):
        # Store the original path
        original_path = request.path

        # Call the function
        decode_url_params()

        # Verify no changes were made since there's no % in path
        assert g.original_url == "/el/wordform/test"
        assert request.path == original_path


# Integration tests with Flask app
def test_integration_greek_characters(client):
    """Test that Greek characters in URLs are properly handled."""
    # Greek word "δοκιμή" (test)
    greek_word = "δοκιμή"
    encoded_word = urllib.parse.quote(greek_word)

    # Make request with encoded word
    response = client.get(f"/el/wordform/{encoded_word}")

    # Check that the response contains the decoded word or is a valid 404
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        html = response.data.decode()
        assert greek_word in html


def test_integration_double_encoded_characters(client):
    """Test that double-encoded Greek characters are properly handled."""
    # Greek word "δοκιμή" (test) double-encoded
    greek_word = "δοκιμή"
    encoded_word = urllib.parse.quote(greek_word)
    double_encoded = urllib.parse.quote(encoded_word)

    # Make request with double-encoded word
    response = client.get(f"/el/wordform/{double_encoded}")

    # The middleware should fix the double encoding
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        html = response.data.decode()
        assert greek_word in html
