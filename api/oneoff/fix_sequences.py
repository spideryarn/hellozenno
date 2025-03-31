#!/usr/bin/env python3
"""Fix sequences in Postgres database after data import."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.db_connection import get_db_config, init_db
from db_models import get_models


def fix_sequences(database):
    """Fix sequences for all tables."""
    print("Fixing sequences...")

    # Get all models
    models = get_models()

    for model in models:
        table_name = model._meta.table_name
        print(f"\nFixing sequence for table: {table_name}")

        try:
            # Get the current max id
            query = f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', 'id'),
                COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1,
                false
            );
            """
            database.execute_sql(query)
            print(f"✓ Successfully fixed sequence for {table_name}")
        except Exception as e:
            print(f"✗ Error fixing sequence for {table_name}: {str(e)}")


def main():
    """Main entry point."""
    # Get database connection
    database = get_db_config()
    init_db(test_db=database)

    try:
        database.connect()
        fix_sequences(database)
        print("\nAll sequences have been fixed!")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        if not database.is_closed():
            database.close()


if __name__ == "__main__":
    main()
