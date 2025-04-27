"""Peewee migrations -- 034_add_userlemma_table.py.

Creates a UserLemma junction table to link users directly to lemmas they've interacted with.
This is similar to ProfileLemma but with a foreign key to auth.users instead of to public.profile.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Create UserLemma table to track user-lemma interactions."""
    
    # Define auth.users model for cross-schema foreign key
    class AuthUser(pw.Model):
        id = pw.UUIDField(primary_key=True)
        
        class Meta:
            table_name = 'users'
            schema = 'auth'
    
    # Define BaseModel for common fields
    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()
        
        class Meta:
            table_name = 'basemodel'
    
    # Define Lemma model - minimal version for foreign key reference
    class Lemma(BaseModel):
        lemma = pw.CharField()
        target_language_code = pw.CharField()
        
        class Meta:
            table_name = 'lemma'
            
    # Define UserLemma junction model
    class UserLemma(BaseModel):
        user_id = pw.UUIDField()  # Reference to auth.users
        lemma = pw.ForeignKeyField(Lemma, backref='user_lemmas')
        ignored_dt = pw.DateTimeField(null=True)  # When lemma was ignored (NULL = not ignored)
        
        class Meta:
            table_name = 'userlemma'
            
    # Create the userlemma table with all fields
    with database.atomic():
        migrator.create_model(UserLemma)
        
        # Add a unique index on (user_id, lemma_id)
        migrator.sql(
            'CREATE UNIQUE INDEX userlemma_user_id_lemma_id_idx ON userlemma (user_id, lemma_id);'
        )
        
        # Add CASCADE deletion for foreign keys
        migrator.sql(
            'ALTER TABLE userlemma DROP CONSTRAINT IF EXISTS userlemma_lemma_id_fkey;'
        )
        migrator.sql(
            'ALTER TABLE userlemma ADD CONSTRAINT userlemma_lemma_id_fkey '
            'FOREIGN KEY (lemma_id) REFERENCES lemma(id) ON DELETE CASCADE;'
        )
        
        # Add the foreign key constraint to auth.users
        migrator.sql(
            """
            ALTER TABLE "userlemma" 
            ADD CONSTRAINT fk_userlemma_user_id
            FOREIGN KEY ("user_id")
            REFERENCES "auth"."users" ("id") 
            ON DELETE CASCADE;
            """
        )
        
        # Add comments explaining the table
        migrator.sql(
            "COMMENT ON TABLE userlemma IS 'Junction table between auth.users and Lemma for tracking user-specific lemma preferences';"
        )
        migrator.sql(
            "COMMENT ON COLUMN userlemma.ignored_dt IS 'When the lemma was ignored (NULL = not ignored)';"
        )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove UserLemma table."""
    
    # Define UserLemma model for rollback
    class UserLemma(pw.Model):
        class Meta:
            table_name = 'userlemma'
            
    with database.atomic():
        # Remove the userlemma table and all its constraints
        migrator.remove_model(UserLemma, cascade=True)