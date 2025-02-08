#!/usr/bin/env python3
"""Database migration script using peewee-migrate."""

import os
import logging
from pathlib import Path
import sys
from peewee_migrate import Router
from db_connection import get_db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peewee_migrate")

# Initialize router with database from db_connection
router = Router(get_db_config(), migrate_dir="migrations")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./migrate.py [create|migrate|list]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create":
        if len(sys.argv) != 3:
            print("Usage: ./migrate.py create <migration_name>")
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
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, migrate, list")
        sys.exit(1)
