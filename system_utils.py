from flask import current_app, g
from playhouse.pool import PooledPostgresqlDatabase
from datetime import datetime
from playhouse.postgres_ext import PostgresqlExtDatabase
import psutil

from views.views import logger


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


def log_db_pool_status():
    """Log database pool status if using a pooled database."""
    db = getattr(g, "db", None)
    if isinstance(db, PostgresqlExtDatabase):
        # Access pool status safely
        pool = getattr(db, "_connection_pool", None)
        if pool:
            current_app.logger.debug("Database pool status: %d connections", len(pool))
