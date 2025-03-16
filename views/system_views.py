from datetime import datetime
import logging
from flask import Blueprint, jsonify

from utils.db_connection import get_db
from utils.env_config import is_vercel

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

        # Get application metrics
        app_metrics = {
            "timestamp": datetime.now().isoformat(),
        }

        # Determine overall status based on database connectivity
        is_healthy = db_metrics["connected"]

        response = {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_metrics,
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


def get_db_metrics(db):
    """Get database metrics.

    Args:
        db: Database connection

    Returns:
        dict: Database metrics
    """
    try:
        # Test database connection with a simple query
        cursor = db.execute_sql("SELECT 1")
        cursor.fetchone()
        cursor.close()

        # Get connection info
        connection_info = {
            "database": db.database,
            "host": db.connect_params.get("host", "unknown"),
            "port": db.connect_params.get("port", "unknown"),
        }

        return {
            "connected": True,
            "connection_info": connection_info,
        }
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return {
            "connected": False,
            "error": str(e),
        }
