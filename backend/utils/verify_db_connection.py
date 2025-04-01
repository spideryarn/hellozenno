#!/usr/bin/env python3
"""Script to verify database connection and basic operations.

This script verifies database connectivity by attempting to connect and run basic queries.
It can be used to test both local and production database connections based on your
environment configuration.

Usage:
    1. Local database testing:
       ```
       PYTHONPATH=.python utils/verify_db_connection.py
       ```
       Uses settings from .env.local by default

    2. Production database testing:
       ```
       source ./scripts/export_envs.sh .env.local_to_prod
       PYTHONPATH=. python tests/backend/verify_db_connection.py
       ```
       Uses settings from .env.local_to_prod to connect to production database

Note:
    - When USE_LOCAL_TO_PROD=1, this connects directly to the production database
      from your local machine. Use with caution.
    - The script will display connection details and run basic queries to verify
      database access.
    - Exit code 0 indicates success, 1 indicates failure.
"""

import logging
import sys
from db_connection import (
    init_db,
    database,
    get_db_config,
    parse_database_url,
)
from env_config import is_local_to_prod, DATABASE_URL
from db_models import get_models
from config import DB_POOL_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection_info():
    """Get sanitized connection information for logging."""
    url = DATABASE_URL.get_secret_value()
    return {
        **parse_database_url(url),
        "mode": "production" if is_local_to_prod() else "local",
    }


def verify_connection():
    """Verify database connection and basic operations."""
    try:
        # Log connection info
        conn_info = get_connection_info()
        logger.info("Connection details:")
        logger.info(f"  Mode: {conn_info['mode']}")
        logger.info(f"  Host: {conn_info['host']}")
        logger.info(f"  Port: {conn_info['port']}")
        logger.info(f"  Database: {conn_info['database']}")
        logger.info(f"  User: {conn_info['user']}")

        if conn_info["mode"] == "production":
            logger.warning("\n⚠️  CONNECTING TO PRODUCTION DATABASE - Use with caution!")

        # Initialize database using shared configuration
        logger.info("\nInitializing database connection...")
        init_db()
        db = get_db_config()  # Get fresh database instance

        # Test connection
        logger.info("Testing connection...")
        db.connect()
        logger.info("✓ Connection successful")

        # Log pool status if using connection pool
        if hasattr(db, "_connections"):
            logger.info("\nConnection pool status:")
            logger.info(f"  Active connections: {len(db._connections)}")
            logger.info(f"  Max connections: {DB_POOL_CONFIG['max_connections']}")

        # Get model list
        models = get_models()
        logger.info(f"\nFound {len(models)} models")

        # Test a simple query on each model
        for model in models:
            logger.info(f"Testing query on {model.__name__}...")
            count = model.select().count()
            logger.info(f"✓ {model.__name__} has {count} records")

            # Update pool status after each query if using connection pool
            if hasattr(db, "_connections"):
                logger.debug(f"  Pool status: {len(db._connections)} connections")

        logger.info("\nAll verifications completed successfully! 🎉")
        return True

    except Exception as e:
        logger.error(f"\nError during verification: {str(e)}")
        return False
    finally:
        if db and not db.is_closed():
            db.close()
            # Final pool status
            if hasattr(db, "_connections"):
                logger.info(f"\nFinal pool status: {len(db._connections)} connections")


if __name__ == "__main__":
    success = verify_connection()
    sys.exit(0 if success else 1)
