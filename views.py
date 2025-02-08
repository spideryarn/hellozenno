from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_from_directory,
    g,
    current_app,
)
from datetime import datetime
import psutil
import logging
from playhouse.pool import PooledPostgresqlDatabase
from playhouse.postgres_ext import PostgresqlExtDatabase
import os

from flask_view_utils import redirect_to_view

from lang_utils import get_all_languages, get_language_name
from wordform_views import get_wordform_metadata, wordform_views_bp
from db_connection import get_db


views_bp = Blueprint("views", __name__)

# Configure logging
logger = logging.getLogger(__name__)


def get_system_metrics():
    """Get system metrics for health check."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage("/").total,
            "free": psutil.disk_usage("/").free,
            "percent": psutil.disk_usage("/").percent,
        },
    }


def get_db_metrics(db):
    """Get database metrics for health check."""
    try:
        # Time the database query
        start_time = datetime.now()
        db.execute_sql("SELECT 1")
        query_time = (datetime.now() - start_time).total_seconds()

        # Get connection pool stats if available
        pool_stats = {}
        if isinstance(db, PooledPostgresqlDatabase):
            pool_stats = {
                "max_connections": getattr(db, "_max_connections", None),
                "stale_timeout": getattr(db, "_stale_timeout", None),
                "timeout": getattr(db, "_timeout", None),
            }

        return {"connected": True, "latency_seconds": query_time, "pool": pool_stats}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"connected": False, "error": str(e)}


@views_bp.route("/health-check")
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


@views_bp.route("/")
def home():
    return redirect_to_view(views_bp, languages)


@views_bp.route("/languages")
def languages():
    supported_languages = get_all_languages()
    return render_template(
        "languages.jinja",
        languages=supported_languages,
    )


@views_bp.route("/<target_language_code>/search")
def search_landing(target_language_code: str):
    """Landing page for word search with a search form."""
    # Get the search query from URL parameters if it exists
    query = request.args.get("q", "")

    if query:
        # If there's a query, redirect to the search endpoint
        return redirect_to_view(
            views_bp,
            search_word,
            target_language_code=target_language_code,
            wordform=query,
        )

    return render_template(
        "search.jinja",
        target_language_code=target_language_code,
        target_language_name=get_language_name(target_language_code),
    )


@views_bp.route("/<target_language_code>/search/<wordform>")
def search_word(target_language_code: str, wordform: str):
    """
    Search for a word and redirect to the wordform view.
    Currently just redirects to the wordform view, but can be enhanced in the future
    to support more sophisticated search functionality.
    """
    return redirect_to_view(
        wordform_views_bp,
        get_wordform_metadata,
        target_language_code=target_language_code,
        wordform=wordform,
    )


@views_bp.route("/favicon.ico/")
def favicon_with_trailing_slash():
    """Handle favicon.ico requests with trailing slash."""
    return send_from_directory(
        os.path.join(views_bp.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def log_db_pool_status():
    """Log database pool status if using a pooled database."""
    db = getattr(g, "db", None)
    if isinstance(db, PostgresqlExtDatabase):
        current_app.logger.debug(
            "Database pool status: %d connections", len(db._connections)
        )
