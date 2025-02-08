#!/usr/bin/env python3
"""Mark a single migration as done without running it."""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from peewee_migrate import Router
from db_connection import get_db_config, init_db
from peewee import SqliteDatabase


def check_migration_exists(migration_name: str) -> bool:
    """Check if migration file exists (including .disabled)."""
    migrations_dir = project_root / "migrations"
    return any(
        migrations_dir.glob(f"{migration_name}.py*")  # Matches .py and .py.disabled
    )


def mark_migration_done(migration_name: str, dry_run: bool = False):
    """Mark a single migration as done without running it."""
    if not check_migration_exists(migration_name):
        print(f"Error: Migration {migration_name} not found")
        sys.exit(1)

    database = get_db_config()
    init_db(test_db=database)

    # Get connection info in a database-agnostic way
    if isinstance(database, SqliteDatabase):
        print(f"Connected to SQLite database: {database.database}")
    else:
        cursor = database.execute_sql(
            "SELECT current_database(), current_user, inet_server_addr(), inet_server_port()"
        )
        db_name, user, host, port = cursor.fetchone()
        print(f"Connected to database: {db_name}")
        print(f"User: {user}")
        print(f"Host: {host}")
        print(f"Port: {port}")

    if dry_run:
        print(f"Would mark migration {migration_name} as done")
        return

    # Ensure database is connected
    if database.is_closed():
        database.connect()

    try:
        router = Router(database, migrate_dir=str(project_root / "migrations"))

        # Manually insert the migration record if it doesn't exist
        if migration_name not in router.done:
            database.execute_sql(
                "INSERT INTO migratehistory (name, migrated_at) VALUES (?, ?)",
                (migration_name, datetime.now()),
            )
            print(f"Marked {migration_name} as done")
        else:
            print(f"Migration {migration_name} was already marked as done")
    finally:
        if not database.is_closed():
            database.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("migration_name", help="Name of migration to mark as done")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without doing it",
    )
    args = parser.parse_args()

    mark_migration_done(args.migration_name, args.dry_run)


if __name__ == "__main__":
    main()
