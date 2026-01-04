"""Error handling utilities for safe error responses."""

from flask import current_app, jsonify
from loguru import logger


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
