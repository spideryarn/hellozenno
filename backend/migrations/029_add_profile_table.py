"""Peewee migrations -- 029_add_profile_table.py.

Creates the profile table for user profiles linked to Supabase auth.users.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Create profile table for Supabase auth integration."""
    
    # Define BaseModel for common fields
    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()
        
        class Meta:
            table_name = 'basemodel'
    
    # Define Profile model - minimal version with just target_language_code
    class Profile(BaseModel):
        user_id = pw.CharField(unique=True)
        target_language_code = pw.CharField(null=True)
        
        class Meta:
            table_name = 'profile'
    
    # Create profile table with all fields
    with database.atomic():
        # Create the profile table - This will automatically create a unique index for user_id
        # since we defined user_id as CharField(unique=True)
        migrator.create_model(Profile)
        
        # Log what's happening - we won't create an explicit index since it's already created
        print("DEBUGGING: Profile table created with implicit index on user_id")
        
        # Add a comment explaining the table's purpose
        migrator.sql(
            "COMMENT ON TABLE profile IS 'User profiles linked to Supabase auth.users';"
        )
        
        # Add a comment explaining user_id reference
        migrator.sql(
            "COMMENT ON COLUMN profile.user_id IS 'References auth.users.id in Supabase';"
        )
        
        # Add a trigger to update the updated_at timestamp
        migrator.sql("""
            CREATE OR REPLACE FUNCTION update_profile_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        migrator.sql("""
            CREATE TRIGGER update_profile_timestamp
            BEFORE UPDATE ON profile
            FOR EACH ROW
            EXECUTE PROCEDURE update_profile_timestamp();
        """)


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove profile table."""
    
    # Define Profile model for rollback
    class Profile(pw.Model):
        class Meta:
            table_name = 'profile'
    
    with database.atomic():
        # Drop the trigger first
        migrator.sql("DROP TRIGGER IF EXISTS update_profile_timestamp ON profile;")
        
        # Remove the profile table and all its constraints
        migrator.remove_model(Profile, cascade=True)
