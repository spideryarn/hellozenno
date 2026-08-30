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
    args = sys.argv[2:]
    # Flags are validated per-command, and every command rejects what it does not
    # implement. A flag that is merely ignored is the accident this guards against:
    # `migrate --dry-run` used to apply every pending migration for real, and a
    # `--dry-run` waved through to `rollback` would likewise roll back for real.
    dry_run = "--dry-run" in args
    if dry_run and command != "migrate":
        print(f"--dry-run is only supported for 'migrate', not '{command}'")
        sys.exit(1)
    unknown = [a for a in args if a.startswith("-") and a != "--dry-run"]
    if unknown:
        print(f"Unknown option(s): {' '.join(unknown)}")
        sys.exit(1)

    if command == "create":
        # Guard the name separately: `create --dry-run` otherwise satisfies the arity
        # check and writes a migration file literally called "--dry-run".
        if len(args) != 1 or args[0].startswith("-"):
            print("Usage: ./utils/migrate.py create <migration_name>")
            sys.exit(1)
        router.create(args[0])
    elif command == "migrate":
        if dry_run:
            # router.diff reads router.done, which initialises peewee-migrate's history
            # model and CREATEs the migratehistory table. On a fresh database that would
            # make the preview itself mutate, so scan the filesystem instead: with no
            # history table, nothing has been applied and everything on disk is pending.
            if router.database.table_exists("migratehistory"):
                pending = router.diff
            else:
                pending = router.todo
            if not pending:
                print("No pending migrations.")
            else:
                print(f"\nWould apply {len(pending)} migration(s):")
                for migration in pending:
                    print(f"⋯ {migration}")
                print()
        else:
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
