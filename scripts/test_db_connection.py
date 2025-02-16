#!/usr/bin/env python3
"""Test script to verify database connection and basic operations."""

import logging
import sys
from utils.db_connection import init_db, database
from db_models import get_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Test database connection and basic operations."""
    try:
        # Initialize database
        logger.info("Initializing database connection...")
        init_db()

        # Test connection
        logger.info("Testing connection...")
        database.connect()
        logger.info("✓ Connection successful")

        # Get model list
        models = get_models()
        logger.info(f"Found {len(models)} models")

        # Test a simple query on each model
        for model in models:
            logger.info(f"Testing query on {model.__name__}...")
            count = model.select().count()
            logger.info(f"✓ {model.__name__} has {count} records")

        logger.info("All tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return False
    finally:
        if database and not database.is_closed():
            database.close()


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
