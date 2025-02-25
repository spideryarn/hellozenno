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

    # Get the Wordform model dynamically
    Wordform = migrator.orm["wordform"]

    # Get all wordforms
    wordforms = Wordform.select()

    # Convert each wordform to NFC and update if different
    update_count = 0
    for wf in wordforms:
        if wf.wordform is None:
            continue

        nfc_form = ensure_nfc(wf.wordform)
        if nfc_form != wf.wordform:
            update_count += 1
            wf.wordform = nfc_form
            wf.save()

    # Log the number of updates
    print(f"Standardized {update_count} wordforms to NFC normalization")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Rollback is a no-op since we don't want to revert to inconsistent normalization."""
    pass  # No rollback needed; this is a data standardization
