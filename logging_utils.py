import json
from datetime import datetime
import logging
import sys
from typing import Optional


def setup_logging(for_cloud: Optional[bool] = False) -> logging.Logger:
    """Configure logging, with special handling for Google Cloud Logging if specified.

    Args:
        for_cloud: If True, configures logging for Google Cloud Logging format
    """
    # Clear any existing handlers
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    # Set the basic config
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(message)s" if for_cloud else "%(asctime)s - %(levelname)s - %(message)s"
        ),
        stream=sys.stdout if for_cloud else sys.stderr,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if for_cloud:
        # Create a custom handler with our JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())

        # Replace the basic handler with our custom one
        root.handlers = [handler]

        # Set Flask's logger to use the same configuration
        flask_logger = logging.getLogger("werkzeug")
        flask_logger.handlers = [handler]

    return logging.getLogger(__name__)


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON formatted logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log records as JSON with additional fields."""
        # Basic message structure
        message = {
            "severity": record.levelname,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add error information if present
        if record.exc_info:
            message["error"] = super().formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, "fields"):  # type: ignore
            message.update(record.fields)  # type: ignore

        return json.dumps(message)
