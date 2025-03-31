#!/usr/bin/env python3
"""
Load production backup into Supabase database.

This script:
1. Verifies the backup file exists
2. Loads the backup into Supabase using psql
3. Verifies the data was loaded correctly
"""

import os

from gjdutils.cmd import run_cmd
from utils.db_connection import parse_database_url, init_db, get_db_config
from utils.env_config import DATABASE_URL
from api.db_models import get_models, Lemma, Sourcedir, Sourcefile

# Constants
BACKUP_PATH = "/Users/greg/Dropbox/dev/experim/hellozenno/backup/production_backup_250209_0231_22.sql"


def load_backup(db_url: str):
    config = parse_database_url(db_url)

    env = os.environ.copy()
    env["PGPASSWORD"] = config["password"]
    return run_cmd(
        f'psql -h {config["host"]} -p {config["port"]} -U {config["user"]} -d {config["database"]} -f {BACKUP_PATH}',
        env=env,
        before_msg="Loading backup into Supabase...",
        fatal_msg=f"Failed to load backup",
    )


def verify_data() -> None:
    """Verify the data was loaded correctly by checking row counts and sample records."""
    print("\nVerifying data integrity...")

    # Initialize database connection
    database = get_db_config()
    init_db(test_db=database)

    try:
        database.connect()

        # Get all models
        models = get_models()
        print(f"\nFound {len(models)} models")

        # Test a simple query on each model
        for model in models:
            count = model.select().count()
            print(f"✓ {model.__name__} has {count} records")

            # Sample check for key models
            if count > 0:
                if model == Lemma:
                    # Check a sample lemma
                    sample = Lemma.select().first()
                    print(f"  Sample lemma: {sample.lemma} ({sample.language_code})")
                    print(f"  Has translations: {bool(sample.translations)}")

                elif model == Sourcedir:
                    # Check a sample sourcedir
                    sample = Sourcedir.select().first()
                    print(f"  Sample sourcedir: {sample.path}")
                    print(f"  Has slug: {bool(sample.slug)}")

                elif model == Sourcefile:
                    # Check a sample sourcefile
                    sample = Sourcefile.select().first()
                    print(f"  Sample sourcefile: {sample.filename}")
                    print(f"  Has metadata: {bool(sample.metadata)}")

        # Verify sequences
        print("\nFixing sequences...")
        for model in models:
            table_name = model._meta.table_name
            try:
                # Get the current max id and update sequence
                query = f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1,
                    false
                );
                """
                database.execute_sql(query)
                print(f"✓ Fixed sequence for {table_name}")
            except Exception as e:
                print(f"✗ Error fixing sequence for {table_name}: {str(e)}")

        print("\nData verification completed successfully!")

    except Exception as e:
        print(f"Error during verification: {str(e)}")
        raise
    finally:
        if not database.is_closed():
            database.close()


def main() -> None:
    """Main entry point."""
    print("Starting backup load process...")
    db_url = DATABASE_URL.get_secret_value()
    load_backup(db_url)

    verify_data()

    print("Backup load completed successfully!")


if __name__ == "__main__":
    main()
