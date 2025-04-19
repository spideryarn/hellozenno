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

from utils.url_registry import endpoint_for

# Import SUPABASE_JWT_SECRET from env_config
from utils.env_config import SUPABASE_JWT_SECRET

# Import Profile model
from db_models import Profile

# Get Supabase JWT Secret from environment - Now imported from env_config
# supabase_jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
# if not supabase_jwt_secret:
#     logger.critical("SUPABASE_JWT_SECRET environment variable not set. Authentication will fail.")
#     # Consider raising an exception or exiting if the secret is critical for startup


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token using the Supabase JWT Secret.

    Args:
        token: JWT token string to verify

    Returns:
        dict: The decoded JWT payload if valid, None otherwise
    """
    # Remove check for secret existence, env_config handles it
    # if not supabase_jwt_secret:
    #     logger.error("JWT Secret not configured. Cannot verify token.")
    #     return None

    try:
        # Decode and verify the token using the JWT Secret
        # Specify HS256 algorithm and verify audience 'authenticated'
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET.get_secret_value(),  # Use the imported secret
            algorithms=["HS256"],  # Use HS256 algorithm
            audience="authenticated",  # Verify audience
            options={
                "verify_exp": True,
                # Remove verify_aud: False, it's handled by the audience parameter
            },
        )

        return payload

    except jwt.exceptions.DecodeError as e:
        logger.warning(f"Invalid token signature or structure: {e}")
        return None
    except jwt.exceptions.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    # Catch specific audience error
    except jwt.exceptions.InvalidAudienceError:
        logger.warning("Invalid JWT audience")
        return None
    except jwt.exceptions.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        # Catch potential errors during key fetching by PyJWKClient - No longer relevant
        logger.error(f"Error verifying JWT token: {e}")
        return None


def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from the Authorization header.

    Checks for token in 'Authorization: Bearer <token>'.

    Returns:
        str: JWT token if found, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
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
        "role": payload.get("role"),
    }

    return user_data


def api_auth_required(f: Callable) -> Callable:
    """Decorator for API endpoints that require authentication.

    If authentication fails, returns a 401 Unauthorized response.
    Otherwise, sets g.user with the authenticated user data from the JWT
    and g.profile with the corresponding Profile record (creating it if necessary).

    Args:
        f: The function to decorate

    Returns:
        The decorated function
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow CORS preflight requests (OPTIONS) to pass through without auth
        if request.method == "OPTIONS":
            return make_response()  # Return empty 200 OK for OPTIONS

        user = get_current_user()  # Gets user data from verified JWT

        if not user or not user.get("id") or not user.get("email"):
            logger.warning("API auth failed: No user data or missing id/email in JWT.")
            return jsonify({"error": "Unauthorized"}), 401

        # Store JWT user info in Flask's g object
        g.user = user

        # Get or create the user profile in our database
        try:
            # Call the custom class method, passing email for logging if needed
            profile, created = Profile.get_or_create_for_user(
                user_id=user["id"], email=user["email"]
            )
            if created:
                logger.info(f"Created new profile for user_id: {user['id']}")
            g.profile = profile
        except Exception as e:
            # Log the error and return an internal server error
            logger.error(
                f"Failed to get or create profile for user {user.get('id')}: {e}"
            )
            return (
                jsonify({"error": "Internal Server Error during profile retrieval"}),
                500,
            )

        return f(*args, **kwargs)

    return decorated
