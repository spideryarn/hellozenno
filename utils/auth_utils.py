"""Authentication utilities for Supabase JWT verification."""

import os
import json
import time
import requests
from functools import wraps
from typing import Optional, Dict, Any, Callable
import jwt
from loguru import logger
from flask import request, redirect, url_for, g, jsonify, make_response

# Cache for Supabase public key
_supabase_public_key = None
_supabase_public_key_last_fetched = 0
_REFRESH_INTERVAL = 3600  # Refresh key every hour


def get_supabase_public_key() -> Optional[str]:
    """Fetch and cache Supabase's public key for JWT verification.
    
    Returns:
        str: The public key as a string, or None if unable to fetch
    """
    global _supabase_public_key, _supabase_public_key_last_fetched
    
    # Get Supabase URL from environment
    supabase_url = os.environ.get("SUPABASE_URL")
    if not supabase_url:
        logger.error("SUPABASE_URL environment variable not set")
        return None
    
    # Check if we need to fetch or refresh the key
    now = time.time()
    if (_supabase_public_key is None or 
        now - _supabase_public_key_last_fetched > _REFRESH_INTERVAL):
        try:
            # Construct the JWKS URL
            jwks_url = f"{supabase_url}/auth/v1/jwks"
            
            # Make the request
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            
            # Parse the JWKS response
            jwks = response.json()
            if not jwks.get("keys") or len(jwks["keys"]) == 0:
                logger.error("No keys found in JWKS response")
                return None
            
            # Get the first key (there's usually only one)
            key_data = jwks["keys"][0]
            
            # Convert JWK to PEM format
            _supabase_public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
            _supabase_public_key_last_fetched = now
            
            logger.info("Successfully fetched Supabase public key")
            return _supabase_public_key
            
        except Exception as e:
            logger.error(f"Error fetching Supabase public key: {e}")
            return None
    
    return _supabase_public_key


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token using Supabase's public key.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        dict: The decoded JWT payload if valid, None otherwise
    """
    try:
        # Get the public key
        public_key = get_supabase_public_key()
        if not public_key:
            logger.error("No public key available for JWT verification")
            return None
            
        # Verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        return None


def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers or cookies.
    
    Checks for token in the following order:
    1. Authorization header (Bearer token)
    2. Cookie named 'sb-auth-token'
    
    Returns:
        str: JWT token if found, None otherwise
    """
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    # Check cookies
    token = request.cookies.get("sb-auth-token")
    if token:
        return token
    
    return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user from the request.
    
    Returns:
        dict: User data if authenticated, None otherwise
    """
    token = extract_token_from_request()
    if not token:
        return None
    
    payload = verify_jwt_token(token)
    if not payload:
        return None
    
    # Extract user data from the token payload
    user_data = {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "app_metadata": payload.get("app_metadata", {}),
        "user_metadata": payload.get("user_metadata", {}),
        "aud": payload.get("aud"),
        "role": payload.get("role")
    }
    
    return user_data


def api_auth_required(f: Callable) -> Callable:
    """Decorator for API endpoints that require authentication.
    
    If authentication fails, returns a 401 Unauthorized response.
    Otherwise, sets g.user with the authenticated user data.
    
    Args:
        f: The function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Store user info in Flask's g object
        g.user = user
        return f(*args, **kwargs)
        
    return decorated


def page_auth_required(f: Callable) -> Callable:
    """Decorator for page routes that require authentication.
    
    If authentication fails, redirects to the auth page.
    Otherwise, sets g.user with the authenticated user data.
    
    Args:
        f: The function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            # For non-API routes, redirect to login page
            target_language_code = kwargs.get("target_language_code")
            # Only include target_language_code if it's a valid non-empty value
            if target_language_code:
                login_url = url_for("system_views.auth_page", target_language_code=target_language_code)
            else:
                login_url = url_for("system_views.auth_page")
            return redirect(login_url)
            
        # Store user info in Flask's g object
        g.user = user
        return f(*args, **kwargs)
        
    return decorated


def set_auth_cookie(token: str, max_age: int = 3600) -> None:
    """Set an HTTP-only cookie with the auth token.
    
    Args:
        token: JWT token string
        max_age: Cookie max age in seconds, defaults to 1 hour
    """
    response = make_response()
    response.set_cookie(
        "sb-auth-token",
        token,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    return response


def clear_auth_cookie() -> None:
    """Clear the auth token cookie."""
    response = make_response()
    response.delete_cookie("sb-auth-token")
    return response