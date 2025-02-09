from datetime import datetime
import logging
import psutil
from flask import Blueprint, jsonify

from db_connection import get_db
from system_utils import get_db_metrics, get_system_metrics

# Create blueprint for system views
system_views_bp = Blueprint("system_views", __name__, url_prefix="/")

# Configure logging
logger = logging.getLogger(__name__)


@system_views_bp.route("health-check")
def health_check():
    """Health check endpoint that verifies app and database functionality."""
    try:
        # Get database metrics
        db = get_db()
        db_metrics = get_db_metrics(db)

        # Get system metrics
        system_metrics = get_system_metrics()

        # Get application metrics
        app_metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": psutil.boot_time(),
        }

        # Determine overall status
        is_healthy = (
            db_metrics["connected"]
            and system_metrics["memory"]["percent"] < 90
            and system_metrics["disk"]["percent"] < 90
        )

        response = {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_metrics,
            "system": system_metrics,
            "application": app_metrics,
        }

        # Log metrics for monitoring
        logger.info("Health check metrics: %s", response)

        return jsonify(response), 200 if is_healthy else 500

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )
