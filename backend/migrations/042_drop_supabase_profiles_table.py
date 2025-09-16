"""Peewee migrations -- 042_drop_supabase_profiles_table.py.

Drops the Supabase starter 'public.profiles' table; the app uses 'public.profile'.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext  # noqa: F401


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Drop the unused Supabase starter 'public.profiles' table."""
    with database.atomic():
        # Drop trigger only if the table exists; dropping a trigger requires the table
        migrator.sql(
            """
            DO $$
            BEGIN
                IF to_regclass('public.profiles') IS NOT NULL THEN
                    EXECUTE 'DROP TRIGGER IF EXISTS handle_profiles_updated_at ON "public"."profiles";';
                END IF;
            END
            $$;
            """
        )
        # Drop the table
        migrator.sql('DROP TABLE IF EXISTS "public"."profiles" CASCADE;')


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Recreate the 'public.profiles' table (minimal schema) if rollback is needed."""
    with database.atomic():
        # Recreate table with minimal fields and constraints
        migrator.sql(
            """
            CREATE TABLE IF NOT EXISTS "public"."profiles" (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id uuid NOT NULL,
                preferences jsonb DEFAULT '{}'::jsonb,
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            );
            """
        )
        migrator.sql(
            'ALTER TABLE "public"."profiles" '
            'ADD CONSTRAINT profiles_user_id_key UNIQUE ("user_id");'
        )
        migrator.sql(
            'ALTER TABLE "public"."profiles" '
            "ADD CONSTRAINT profiles_user_id_fkey "
            'FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;'
        )
        migrator.sql(
            "CREATE INDEX IF NOT EXISTS idx_profiles_user_id "
            'ON "public"."profiles" ("user_id");'
        )
        # Optionally restore updated_at trigger if moddatetime() exists
        migrator.sql(
            """
            DO $$
            BEGIN
                PERFORM 1
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE p.proname = 'moddatetime';
                IF FOUND THEN
                    EXECUTE 'CREATE TRIGGER handle_profiles_updated_at '
                            'BEFORE UPDATE ON "public"."profiles" '
                            'FOR EACH ROW EXECUTE FUNCTION moddatetime(''updated_at'');';
                END IF;
            END
            $$;
            """
        )
