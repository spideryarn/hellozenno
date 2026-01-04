"""URL encoding and decoding utilities."""

import ipaddress
import os
import socket
import urllib.parse
from flask import request, g, url_for
from loguru import logger


class SSRFValidationError(Exception):
    """Raised when URL fails SSRF validation."""
    pass


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private or
            ip.is_loopback or
            ip.is_reserved or
            ip.is_link_local or
            ip.is_multicast
        )
    except ValueError:
        return False


LOCALHOST_VARIANTS = frozenset({
    "localhost", "127.0.0.1", "::1", "0.0.0.0",
    "localhost.localdomain", "127.0.0.0", "[::1]"
})


def validate_url_for_ssrf(url: str) -> str:
    """Validate a URL for SSRF vulnerabilities.
    
    Checks:
    - Scheme is http or https only
    - Host is not localhost or private IP
    - Host doesn't resolve to private IP
    
    Returns the validated URL if safe.
    Raises SSRFValidationError if URL fails validation.
    """
    if not url:
        raise SSRFValidationError("URL is required")
    
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        raise SSRFValidationError(f"Invalid URL format: {e}")
    
    if parsed.scheme not in ("http", "https"):
        raise SSRFValidationError(f"Invalid scheme: {parsed.scheme}. Only http/https allowed.")
    
    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("URL must include a hostname")
    
    if hostname.lower() in LOCALHOST_VARIANTS:
        raise SSRFValidationError("Localhost URLs are not allowed")
    
    # Check if hostname is an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        if is_private_ip(hostname):
            raise SSRFValidationError("Private IP addresses are not allowed")
    except ValueError:
        pass  # Not an IP, proceed to DNS resolution
    
    # Resolve hostname and check resulting IP
    try:
        default_port = 443 if parsed.scheme == "https" else 80
        resolved_ips = socket.getaddrinfo(hostname, parsed.port or default_port)
        for family, type_, proto, canonname, sockaddr in resolved_ips:
            ip = sockaddr[0]
            if is_private_ip(ip):
                logger.warning(f"SSRF blocked: {hostname} resolves to private IP {ip}")
                raise SSRFValidationError("URL resolves to private IP address")
    except socket.gaierror:
        raise SSRFValidationError(f"Could not resolve hostname: {hostname}")
    except SSRFValidationError:
        raise
    except Exception as e:
        logger.error(f"SSRF validation error for {url}: {e}")
        raise SSRFValidationError(f"URL validation failed: {e}")
    
    return url


def fix_url_encoding(url_part):
    """
    Fix URL encoding issues with non-Latin characters.

    This handles the case where a URL part might be double-encoded
    or encoded with the wrong charset.

    Args:
        url_part (str): The URL part to fix

    Returns:
        str: The properly decoded URL part
    """
    # If the URL part contains percent-encoded sequences that might be double-encoded
    if "%25" in url_part:
        # URL is double-encoded, decode it once
        return urllib.parse.unquote(url_part)

    # If the URL part contains percent-encoded sequences
    if "%" in url_part:
        try:
            # Try to decode as UTF-8
            return urllib.parse.unquote(url_part)
        except UnicodeDecodeError:
            # If that fails, try the Latin-1 to UTF-8 conversion
            return url_part.encode("iso-8859-1").decode("utf-8", errors="replace")

    return url_part


def decode_url_params():
    """
    Decode URL path and query parameters to handle Unicode characters properly.

    This function is designed to be used as a Flask before_request middleware.
    It intercepts all requests and fixes URL encoding issues with non-Latin characters.
    """
    # Store the original URL for logging
    g.original_url = request.path

    # Check if the URL contains percent-encoded sequences
    if "%" in request.path:
        # Fix URL encoding
        decoded_path = fix_url_encoding(request.path)
        if decoded_path != request.path:
            logger.info(f"Fixed URL encoding: {request.path} -> {decoded_path}")
            request.path = decoded_path


def url_with_query(endpoint, _query_parameters=None, **kwargs):
    """Generate a URL with both path parameters and query parameters.

    This function extends Flask's url_for to handle query parameters separately.

    Args:
        endpoint: The endpoint to generate a URL for (can be a string or function)
        _query_parameters: A dictionary of query parameters to append
        **kwargs: Path parameters to pass to url_for

    Returns:
        str: The URL with both path and query parameters

    Example:
        url_with_query(wordforms_list, {'sort': 'frequency'}, target_language_code='el')
        # Returns "/lang/el/wordforms?sort=frequency"
    """
    base_url = url_for(endpoint, **kwargs)

    if not _query_parameters:
        return base_url

    query_string = urllib.parse.urlencode(_query_parameters)
    return f"{base_url}?{query_string}"


def load_vite_manifest():
    """Load the Vite manifest file for asset versioning."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check both possible manifest locations
    manifest_paths = [
        os.path.join(root_dir, "static/build/.vite/manifest.json"),  # Original location
        os.path.join(root_dir, "static/build/manifest.json"),  # Copied location
    ]

    try:
        import json

        # Try each path in order
        for manifest_path in manifest_paths:
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    logger.info(f"Loaded Vite manifest from {manifest_path}")
                    return json.load(f)

        # If we get here, neither file was found
        logger.warning(f"Vite manifest not found in any of: {manifest_paths}")
        return {}
    except Exception as e:
        logger.error(f"Error loading Vite manifest: {e}")
        return {}
