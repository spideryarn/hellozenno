"""Peewee migrations -- 019_standardize_unicode_normalization.py.

Standardize all wordforms in the database to use NFC (Normalization Form C) Unicode.
This ensures consistent handling of diacritics across the application by converting
any decomposed forms (NFD) to composed forms (NFC).
"""

import unicodedata
from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def ensure_nfc(text):
    """Ensure text is in NFC (Normalization Form C) for consistent handling."""
    if text is None:
        return None
    return unicodedata.normalize("NFC", text)


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Standardize all wordforms to NFC normalization."""
    if fake:
        return

    # Use raw SQL to update the wordforms directly
    with database.atomic():
        duplicate_pairs = []

        # First, find all pairs of duplicates where normalizing would create conflicts
        cursor = database.execute_sql(
            "SELECT id, wordform, language_code FROM wordform WHERE wordform IS NOT NULL"
        )

        for row in cursor.fetchall():
            wf_id, wordform, language_code = row
            nfc_form = ensure_nfc(wordform)

            # Skip if already in NFC form
            if nfc_form == wordform:
                continue

            # Check if normalizing would create a duplicate
            check_cursor = database.execute_sql(
                "SELECT id FROM wordform WHERE wordform = %s AND language_code = %s AND id != %s",
                (nfc_form, language_code, wf_id),
            )
            existing = check_cursor.fetchone()

            if existing:
                existing_id = existing[0]
                # Found a duplicate pair - id to keep and id to remove
                duplicate_pairs.append((existing_id, wf_id))

        # Handle all duplicates
        for existing_id, duplicate_id in duplicate_pairs:
            # Transfer SourcefileWordform relationships
            migrator.sql(
                """
                INSERT INTO sourcefilewordform (sourcefile_id, wordform_id, centrality, ordering, created_at, updated_at)
                SELECT sourcefile_id, %s, centrality, ordering, NOW(), NOW()
                FROM sourcefilewordform
                WHERE wordform_id = %s
                ON CONFLICT (sourcefile_id, wordform_id) DO NOTHING
                """,
                (existing_id, duplicate_id),
            )

            # Delete the duplicate
            migrator.sql("DELETE FROM wordform WHERE id = %s", (duplicate_id,))

        if duplicate_pairs:
            print(f"Resolved {len(duplicate_pairs)} duplicate wordforms")

        # Now normalize remaining wordforms
        cursor = database.execute_sql(
            "SELECT id, wordform FROM wordform WHERE wordform IS NOT NULL"
        )

        update_count = 0
        for row in cursor.fetchall():
            wf_id, wordform = row
            nfc_form = ensure_nfc(wordform)

            if nfc_form != wordform:
                update_count += 1
                # Use migrator.sql for updates
                migrator.sql(
                    "UPDATE wordform SET wordform = %s WHERE id = %s", (nfc_form, wf_id)
                )

        # Log the number of updates
        print(f"Standardized {update_count} wordforms to NFC normalization")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Rollback is a no-op since we don't want to revert to inconsistent normalization."""
    pass  # No rollback needed; this is a data standardization
