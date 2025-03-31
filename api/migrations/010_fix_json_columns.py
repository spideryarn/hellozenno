"""Fix JSON columns to use JSONB type."""

from playhouse.migrate import PostgresqlMigrator


def migrate(migrator: PostgresqlMigrator, database, fake=False):
    """Convert JSON columns from TEXT to JSONB type."""
    if fake:
        return

    with database.atomic():
        try:
            # Lemma JSON fields
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN translations TYPE JSONB USING translations::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN synonyms TYPE JSONB USING synonyms::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN antonyms TYPE JSONB USING antonyms::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN related_words_phrases_idioms TYPE JSONB USING related_words_phrases_idioms::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN mnemonics TYPE JSONB USING mnemonics::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN easily_confused_with TYPE JSONB USING easily_confused_with::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN example_usage TYPE JSONB USING example_usage::jsonb"
            )

            # Wordform JSON fields
            database.execute_sql(
                "ALTER TABLE wordform ALTER COLUMN translations TYPE JSONB USING translations::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE wordform ALTER COLUMN possible_misspellings TYPE JSONB USING possible_misspellings::jsonb"
            )

            # Sentence JSON fields
            database.execute_sql(
                "ALTER TABLE sentence ALTER COLUMN lemma_words TYPE JSONB USING lemma_words::jsonb"
            )

            # Phrase JSON fields
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN raw_forms TYPE JSONB USING raw_forms::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN translations TYPE JSONB USING translations::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN mnemonics TYPE JSONB USING mnemonics::jsonb"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN component_words TYPE JSONB USING component_words::jsonb"
            )

            # Sourcefile JSON fields
            database.execute_sql(
                "ALTER TABLE sourcefile ALTER COLUMN metadata TYPE JSONB USING metadata::jsonb"
            )

        except Exception as e:
            database.rollback()
            raise e


def rollback(migrator: PostgresqlMigrator, database, fake=False):
    """Convert JSON columns back to TEXT type."""
    if fake:
        return

    with database.atomic():
        try:
            # Lemma JSON fields
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN translations TYPE TEXT USING translations::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN synonyms TYPE TEXT USING synonyms::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN antonyms TYPE TEXT USING antonyms::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN related_words_phrases_idioms TYPE TEXT USING related_words_phrases_idioms::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN mnemonics TYPE TEXT USING mnemonics::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN easily_confused_with TYPE TEXT USING easily_confused_with::text"
            )
            database.execute_sql(
                "ALTER TABLE lemma ALTER COLUMN example_usage TYPE TEXT USING example_usage::text"
            )

            # Wordform JSON fields
            database.execute_sql(
                "ALTER TABLE wordform ALTER COLUMN translations TYPE TEXT USING translations::text"
            )
            database.execute_sql(
                "ALTER TABLE wordform ALTER COLUMN possible_misspellings TYPE TEXT USING possible_misspellings::text"
            )

            # Sentence JSON fields
            database.execute_sql(
                "ALTER TABLE sentence ALTER COLUMN lemma_words TYPE TEXT USING lemma_words::text"
            )

            # Phrase JSON fields
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN raw_forms TYPE TEXT USING raw_forms::text"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN translations TYPE TEXT USING translations::text"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN mnemonics TYPE TEXT USING mnemonics::text"
            )
            database.execute_sql(
                "ALTER TABLE phrase ALTER COLUMN component_words TYPE TEXT USING component_words::text"
            )

            # Sourcefile JSON fields
            database.execute_sql(
                "ALTER TABLE sourcefile ALTER COLUMN metadata TYPE TEXT USING metadata::text"
            )

        except Exception as e:
            database.rollback()
            raise e
