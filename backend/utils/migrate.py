#!/usr/bin/env python3
"""Database migration script using peewee-migrate."""

import os
import logging
from pathlib import Path
import sys
from peewee_migrate import Router
from utils.db_connection import get_db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peewee_migrate")

# Initialize router with database from db_connection
router = Router(get_db_config(), migrate_dir="migrations")

def list_migrations():
    """Return lists of done and pending migrations."""
    return {
        "done": router.done,
        "pending": router.diff
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./utils/migrate.py [create|migrate|list|rollback]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create":
        if len(sys.argv) != 3:
            print("Usage: ./utils/migrate.py create <migration_name>")
            sys.exit(1)
        router.create(sys.argv[2])
    elif command == "migrate":
        router.run()
    elif command == "list":
        print("\nAvailable migrations:")
        for migration in router.done:
            print(f"✓ {migration}")
        for migration in router.diff:
            print(f"⋯ {migration}")
        print()
    elif command == "rollback":
        # Rollback the latest migration
        if router.done:
            latest_migration = router.done[-1]
            print(f"Rolling back migration: {latest_migration}")
            
            # The rollback method calls the rollback function in the migration file
            router.rollback()
            print(f"Successfully rolled back {latest_migration}")
        else:
            print("No migrations to roll back.")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, migrate, list, rollback")
        sys.exit(1)
