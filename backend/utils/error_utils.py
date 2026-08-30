"""Error handling utilities for safe error responses."""

from flask import current_app, jsonify, make_response, request
from loguru import logger
from playhouse.pool import MaxConnectionsExceeded
from utils.exceptions import DatabaseOverloadedError


def safe_error_message(error: Exception, context: str = "") -> str:
    """Return a safe error message based on environment.
    
    In production: Returns generic message, logs full error with stack trace
    In development: Returns full error details
    """
    is_production = current_app.config.get("IS_PRODUCTION", True)
    
    log_message = f"{context}: {error}" if context else str(error)
    logger.exception(log_message)
    
    if is_production:
        return "An internal error occurred. Please try again later."
    return str(error)


def error_response(error: Exception, status_code: int = 500, context: str = ""):
    """Create a JSON error response with safe error message."""
    message = safe_error_message(error, context)
    return jsonify({"error": message}), status_code


# How long to tell a caller to wait out a pool-exhaustion burst. Matches the pool's
# own connect timeout (config.DB_POOL_CONFIG["timeout"]): by the time we have given
# up waiting, another few seconds is the right order of magnitude to retry in.
POOL_EXHAUSTION_RETRY_AFTER = 5


def register_pool_exhaustion_handler(app):
    """Report connection-pool exhaustion as 503, not 500.

    This is transient overload, not a bug: the pool is capped per function instance,
    so a burst of concurrent anonymous reads can starve an otherwise valid request -
    including a logged-in user's write. Returning 500 made every such failure look
    like a crash and told the caller nothing useful; 503 + Retry-After says "come
    back", which is what a well-behaved client or crawler needs to hear to stop
    retrying immediately and deepening the pile-up.

    Registered as a function so tests can apply it to a bare app - the test client
    builds its own Flask app rather than going through create_app().
    """

    @app.errorhandler(DatabaseOverloadedError)
    @app.errorhandler(MaxConnectionsExceeded)
    def _pool_exhausted(e):
        logger.warning(f"Connection pool exhausted for {request.path}")
        if request.path.startswith("/api/"):
            response = jsonify(
                {
                    "error": "Service temporarily unavailable",
                    "status_code": 503,
                    "message": "The server is briefly over capacity. Please retry.",
                }
            )
        else:
            response = make_response("Service Temporarily Unavailable")
        response.status_code = 503
        response.headers["Retry-After"] = str(POOL_EXHAUSTION_RETRY_AFTER)
        return response

    return app
