"""SUPERSEDED by 004_fix_sourcedir_language.py.

This migration attempted to add language support by:
1. Creating a separate language table
2. Adding language_id to sourcedir as a foreign key

This approach was superseded by 004_fix_sourcedir_language.py which:
1. Adds language_code directly to sourcedir
2. Removes the need for a separate language table
3. Makes the implementation simpler and more maintainable
"""


def migrate(migrator, database, *, fake=False):
    """Migration superseded by 004."""
    pass


def rollback(migrator, database, *, fake=False):
    """No rollback needed as migration is superseded."""
    pass
