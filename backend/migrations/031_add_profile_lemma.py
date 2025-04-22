"""Peewee migrations -- 031_add_profile_lemma.py.

Creates a ProfileLemma junction table to track which lemmas a user has ignored.
"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Create ProfileLemma table to track ignored lemmas."""
    
    # Define BaseModel for common fields
    class BaseModel(pw.Model):
        created_at = pw.DateTimeField()
        updated_at = pw.DateTimeField()
        
        class Meta:
            table_name = 'basemodel'
    
    # Define Profile model - minimal version for foreign key reference
    class Profile(BaseModel):
        user_id = pw.CharField(unique=True)
        
        class Meta:
            table_name = 'profile'
            
    # Define Lemma model - minimal version for foreign key reference
    class Lemma(BaseModel):
        lemma = pw.CharField()
        target_language_code = pw.CharField()
        
        class Meta:
            table_name = 'lemma'
            
    # Define ProfileLemma junction model
    class ProfileLemma(BaseModel):
        profile = pw.ForeignKeyField(Profile, backref='profile_lemmas')
        lemma = pw.ForeignKeyField(Lemma, backref='profile_lemmas')
        ignored_dt = pw.DateTimeField(null=True)  # When lemma was ignored (NULL = not ignored)
        
        class Meta:
            table_name = 'profilelemma'
            
    # Create the profile_lemma table with all fields
    with database.atomic():
        migrator.create_model(ProfileLemma)
        
        # Add a unique index on (profile_id, lemma_id)
        migrator.sql(
            'CREATE UNIQUE INDEX profilelemma_profile_id_lemma_id_idx ON profilelemma (profile_id, lemma_id);'
        )
        
        # Add CASCADE deletion for foreign keys
        migrator.sql(
            'ALTER TABLE profilelemma DROP CONSTRAINT IF EXISTS profilelemma_profile_id_fkey;'
        )
        migrator.sql(
            'ALTER TABLE profilelemma ADD CONSTRAINT profilelemma_profile_id_fkey '
            'FOREIGN KEY (profile_id) REFERENCES profile(id) ON DELETE CASCADE;'
        )
        
        migrator.sql(
            'ALTER TABLE profilelemma DROP CONSTRAINT IF EXISTS profilelemma_lemma_id_fkey;'
        )
        migrator.sql(
            'ALTER TABLE profilelemma ADD CONSTRAINT profilelemma_lemma_id_fkey '
            'FOREIGN KEY (lemma_id) REFERENCES lemma(id) ON DELETE CASCADE;'
        )
        
        # Add comments explaining the table
        migrator.sql(
            "COMMENT ON TABLE profilelemma IS 'Junction table between Profile and Lemma for tracking user-specific lemma preferences';"
        )
        migrator.sql(
            "COMMENT ON COLUMN profilelemma.ignored_dt IS 'When the lemma was ignored (NULL = not ignored)';"
        )
        
        # Let the application handle timestamps - no triggers necessary
        # This is simpler and relies on peewee's functionality for timestamp management


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Remove ProfileLemma table."""
    
    # Define ProfileLemma model for rollback
    class ProfileLemma(pw.Model):
        class Meta:
            table_name = 'profilelemma'
            
    with database.atomic():
        # Remove the profile_lemma table and all its constraints
        migrator.remove_model(ProfileLemma, cascade=True)