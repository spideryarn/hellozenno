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
        # First, get all wordforms that need normalization
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
