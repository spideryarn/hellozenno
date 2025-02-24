#!/usr/bin/env python3
"""
Script to mark all existing migrations as done in the database.
This is useful when the migration history has been lost but the database structure
is already up to date with the migrations.
"""

import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.migrate import list_migrations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mark_migrations")


def mark_migrations_done(dry_run=False):
    """Mark all existing migrations as done in the database."""
    # Get list of all pending migrations
    migrations = list_migrations()
    pending_migrations = migrations["pending"]

    if not pending_migrations:
        print("No pending migrations found.")
        return

    print(f"Found {len(pending_migrations)} migrations to mark as done:")
    for migration in pending_migrations:
        print(f"  - {migration}")

    if dry_run:
        print("\nDRY RUN: No changes will be made to the database.")
        return

    # Mark each migration as done using mark_single_migration_done.py
    for migration in pending_migrations:
        print(f"Marking {migration} as done...")
        script_path = project_root / "oneoff" / "mark_single_migration_done.py"
        cmd = [sys.executable, str(script_path), migration]

        # Run the command and check for errors immediately
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,  # This will raise an exception if the command fails
            )
            print(f"Successfully marked {migration} as done")
        except subprocess.CalledProcessError as e:
            print(f"Error marking {migration} as done:")
            print(e.stderr)
            sys.exit(1)  # Exit immediately on any error

    print("\nAll migrations have been marked as done.")
    print("You can verify with: python -m utils.migrate list")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mark all migrations as done in the database."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )
    args = parser.parse_args()

    mark_migrations_done(dry_run=args.dry_run)
