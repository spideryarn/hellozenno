#!/usr/bin/env python3
"""Fix sourcedir table by adding language_code and updating unique index."""

import sys
from pathlib import Path
from peewee import SqliteDatabase

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.db_connection import get_db_config, init_db


def fix_sourcedir():
    """Fix the sourcedir table structure."""
    database = get_db_config()
    init_db(test_db=database)

    with database.atomic():
        # For SQLite, we need to:
        # 1. Create a new table with the desired schema
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table

        # Create new table
        database.execute_sql(
            """
            CREATE TABLE sourcedir_new (
                id INTEGER NOT NULL PRIMARY KEY,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                path VARCHAR(255) NOT NULL,
                language_code VARCHAR(2) NOT NULL
            );
        """
        )

        # Copy data from old table, setting language_code to 'el'
        database.execute_sql(
            """
            INSERT INTO sourcedir_new (id, created_at, updated_at, path, language_code)
            SELECT id, created_at, updated_at, path, 'el'
            FROM sourcedir;
        """
        )

        # Create the new composite unique index
        database.execute_sql(
            """
            CREATE UNIQUE INDEX sourcedir_new_path_language_code 
            ON sourcedir_new (path, language_code);
        """
        )

        # Drop the old table
        database.execute_sql("DROP TABLE sourcedir;")

        # Rename the new table
        database.execute_sql("ALTER TABLE sourcedir_new RENAME TO sourcedir;")

    print("Successfully updated sourcedir table")


if __name__ == "__main__":
    fix_sourcedir()
