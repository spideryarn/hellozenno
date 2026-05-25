"""Authentication utilities for Supabase JWT verification."""

from functools import wraps
from typing import Optional, Dict, Any, Callable, Tuple
from urllib.parse import urlparse, quote
import jwt
from jwt import PyJWKClient
from loguru import logger
from flask import request, redirect, url_for, g, jsonify, make_response

from utils.url_registry import endpoint_for

from utils.env_config import SUPABASE_URL

from db_models import Profile

_ACCEPTED_ALGORITHMS = ("ES256", "RS256", "EdDSA")

_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> PyJWKClient:
    """Return a cached PyJWKClient pointed at the project's JWKS endpoint.

    Supabase exposes JWT signing keys at /auth/v1/.well-known/jwks.json.
    The legacy HS256 shared-secret path was removed on 2026-05-25 once the
    project finished migrating to the new JWT signing keys system and the
    legacy secret was revoked.
    """
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(
            jwks_url,
            cache_keys=True,
            lifespan=3600,
        )
    return _jwks_client


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a Supabase-issued JWT via the project's JWKS endpoint.

    Only asymmetric algorithms (ES256 / RS256 / EdDSA) are accepted; the
    legacy HS256 shared-secret path was removed when the legacy signing key
    was revoked. Tokens with any other `alg` header are rejected.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "")

        if alg not in _ACCEPTED_ALGORITHMS:
            logger.warning(f"Unsupported JWT algorithm: {alg!r}")
            return None

        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[alg],
            audience="authenticated",
            options={"verify_exp": True},
        )
        return payload

    except jwt.exceptions.DecodeError as e:
        logger.warning(f"Invalid token signature or structure: {e}")
        return None
    except jwt.exceptions.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.exceptions.InvalidAudienceError:
        logger.warning("Invalid JWT audience")
        return None
    except jwt.exceptions.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
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


def _attempt_authentication_and_set_g() -> bool:
    """Attempts to authenticate user from JWT and set g.user, g.user_id, and g.profile.

    Returns:
        bool: True if authentication succeeded (user found), False otherwise.
              Note: Returns True even if profile fetch fails after successful auth.
    """
    user = get_current_user()  # Attempt to get user from verified JWT
    g.user = None  # Initialize
    g.user_id = None  # Initialize
    g.profile = None  # Initialize

    if user and user.get("id") and user.get("email"):
        # User is authenticated
        g.user = user
        g.user_id = user["id"]  # Set user_id directly for UserLemma operations
        try:
            profile_obj, created = Profile.get_or_create_for_user(user_id=user["id"])
            if created:
                logger.info(f"Created new profile for user_id: {user['id']}")
            g.profile = profile_obj
            # Compute admin flag from profile
            try:
                g.is_admin = bool(
                    getattr(g, "profile", None)
                    and getattr(g.profile, "admin_granted_at", None)
                )
            except Exception:
                g.is_admin = False
        except Exception as e:
            # Log profile fetch error, but proceed since user is authenticated
            logger.error(
                f"Failed to get or create profile for authenticated user {user.get('id')}: {e}"
            )
            # g.profile remains None
            g.is_admin = False
        return True  # Authentication successful
    else:
        # Authentication failed or no token provided
        g.is_admin = False
        return False  # Authentication failed


def api_auth_optional(f: Callable) -> Callable:
    """Decorator for API endpoints where authentication is optional.

    Attempts authentication and sets g.user and g.profile if successful.
    Always proceeds with the request, regardless of auth success.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return make_response()

        _attempt_authentication_and_set_g()  # Attempt auth, ignore return value

        # Proceed regardless of whether user was found
        return f(*args, **kwargs)

    return decorated


def api_auth_required(f: Callable) -> Callable:
    """Decorator for API endpoints that require authentication.

    If authentication fails, returns a 401 Unauthorized response.
    Otherwise, sets g.user and g.profile, then proceeds.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return make_response()

        authenticated = _attempt_authentication_and_set_g()

        if not authenticated:
            logger.warning("API auth failed: Required but no valid user found.")
            return jsonify({"error": "Unauthorized"}), 401

        # Check if profile retrieval failed during the attempt (g.profile would be None)
        if g.user and g.profile is None:
            logger.error(
                f"Internal Server Error: Profile retrieval failed for user {g.user.get('id')} during required auth."
            )
            return (
                jsonify({"error": "Internal Server Error during profile retrieval"}),
                500,
            )

        # Proceed if authenticated and profile is available
        return f(*args, **kwargs)

    return decorated


def api_admin_required(f: Callable) -> Callable:
    """Decorator for API endpoints that require admin privileges.

    Requires authentication first (401 if no user), then checks admin flag
    on g.profile (403 if not admin).
    """

    @wraps(f)
    @api_auth_required
    def decorated(*args, **kwargs):
        if not bool(getattr(g, "is_admin", False)):
            return jsonify({"error": "Forbidden", "reason": "not_admin"}), 403
        return f(*args, **kwargs)

    return decorated


# Remove the old complex implementation of api_auth_required that handled required=False


def is_safe_redirect_url(url: str) -> bool:
    """Validate that a redirect URL is safe (relative path only).
    
    Prevents open redirect attacks by blocking absolute URLs with schemes/netlocs.
    """
    if not url:
        return False
    # Block protocol-relative URLs like //evil.com/path
    if url.startswith("//"):
        return False
    parsed = urlparse(url)
    # Only allow relative URLs (no scheme, no netloc) that start with /
    return not parsed.scheme and not parsed.netloc and url.startswith("/")


def page_auth_required(f: Callable) -> Callable:
    """Decorator for page views that require authentication.

    If authentication fails, redirect to the auth page with a next parameter.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        authenticated = _attempt_authentication_and_set_g()
        if not authenticated:
            next_url = request.full_path if request.query_string else request.path
            if not is_safe_redirect_url(next_url):
                next_url = "/"
            return redirect(f"/auth?next={quote(next_url, safe='/')}")
        return f(*args, **kwargs)

    return decorated


def get_user_by_id(user_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Profile]]:
    """Get a user's information by their user ID.

    Args:
        user_id: Supabase auth user ID

    Returns:
        Tuple of (user_data, profile_obj) where:
            - user_data: Contains email and other user information if found, or None
            - profile_obj: The user's Profile object if found, or None
    """
    try:
        # First, try to get the user's profile
        profile_obj = Profile.get_or_none(Profile.user_id == user_id)

        # Next, get the user's auth info from AuthUser (maps to auth.users)
        # Import here to avoid circular imports
        from db_models import AuthUser

        user_data = None
        try:
            auth_user = AuthUser.get_by_id(user_id)
            # Create a user data dict with available fields
            user_data = {
                "id": user_id,
                # Add other fields from auth_user that are accessible
            }

            # Add email if it's available in AuthUser
            if hasattr(auth_user, "email"):
                user_data["email"] = auth_user.email

        except DoesNotExist:
            logger.warning(f"AuthUser not found for user_id: {user_id}")
            # Still create minimal user data if we at least have the ID
            user_data = {"id": user_id} if user_id else None

        if not profile_obj:
            logger.warning(f"Profile not found for user_id: {user_id}")
            # We might want to auto-create a profile here if needed

        return user_data, profile_obj
    except Exception as e:
        logger.error(f"Error retrieving user by ID {user_id}: {e}")
        return None, None
