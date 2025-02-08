# JSON Metadata and PostgreSQL Extension Issue

## Goal Statement
Fix the issue with JSON metadata fields being stored as text instead of JSONB in PostgreSQL, which is causing TypeError when accessing metadata fields. This was discovered when a 500 error occurred in `sourcedir_views.py` while trying to access `sourcefile_entry.metadata["image_processing"]`.

## Scope of Changes
The changes are focused on two necessary components to fix JSON handling:
1. Database Column Types: Converting all JSON fields from TEXT to JSONB type
2. Database Adapter: Switching to `PostgresqlExtDatabase` for proper JSON support

While the changes touch multiple files, they are all related to these two components:
- Migration script only modifies JSON field types
- Database adapter change is the minimum needed for proper JSON handling
- No other schema or functionality changes are included

## Current Status
- Identified that all JSON fields in the database are stored as TEXT instead of JSONB
- Created and tested a migration to convert all JSON fields to JSONB type
- Confirmed the issue exists in both development and production databases
- Successfully tested JSON field handling in test environment
- Ready to execute migration in production environment

## Tasks

### DONE
1. Investigation
   - Confirmed metadata is valid JSON in the database
   - Verified issue is systemic across all records
   - Checked database adapter configuration
   - Identified root cause: using `PooledPostgresqlDatabase` instead of `PostgresqlExtDatabase`

2. Test Development
   - Created test for JSON field handling in `test_db_models.py`
   - Added test for JSON column migration in `test_migrations.py`
   - Verified tests pass with new database configuration

3. Migration Development
   - Created migration script `010_fix_json_columns.py`
   - Implemented forward and rollback migrations
   - Added proper error handling and transactions
   - Tested migration locally

### TODO
1. Production Migration
   - [ ] Take backup of production database
   - [ ] Test migration on copy of production data
   - [ ] Schedule maintenance window
   - [ ] Execute migration on production
   - [ ] Verify application functionality after migration

2. Database Configuration
   - [ ] Update database connection to use `PostgresqlExtDatabase`
   - [ ] Test connection pooling with extended database
   - [ ] Monitor performance after changes

3. Application Testing
   - [ ] Test all routes that use JSON fields
   - [ ] Verify metadata access in sourcefile views
   - [ ] Check JSON field handling in all models

## Technical Details

### Affected Models and Fields
1. Lemma
   - translations (JSONField)
   - synonyms (JSONField)
   - antonyms (JSONField)
   - related_words_phrases_idioms (JSONField)
   - mnemonics (JSONField)
   - easily_confused_with (JSONField)
   - example_usage (JSONField)

2. Wordform
   - translations (JSONField)
   - possible_misspellings (JSONField)

3. Sentence
   - lemma_words (JSONField)

4. Phrase
   - raw_forms (JSONField)
   - translations (JSONField)
   - mnemonics (JSONField)
   - component_words (JSONField)

5. Sourcefile
   - metadata (JSONField)

### Migration Strategy
1. Create new JSONB column
2. Convert existing data using `::jsonb` cast
3. Drop old column
4. Rename new column to original name

### Database Configuration Changes
```python
# Old configuration
database = PooledPostgresqlDatabase(...)

# New configuration
database = PooledPostgresqlExtDatabase(...)
```

### Configuration Management
- Moved hardcoded database configuration from `migrate.py` to central configuration
- Production settings now use `DB_CONFIG` from `config.py`
- Local development settings use environment variables with sensible defaults
- Credentials remain in `_secrets.py`
- Configuration follows the same pattern as the rest of the application

This change:
- Centralizes configuration management
- Makes it easier to modify settings
- Reduces risk of configuration drift
- Follows existing application patterns

## Risks and Mitigations
1. Data Loss
   - Full database backup before migration
   - Transaction wrapping for atomic operations
   - Rollback functionality implemented

2. Production Impact
   - Schedule maintenance window
   - Test migration on copy of production data
   - Monitor application performance

3. Performance
   - Monitor query performance with JSONB
   - Watch connection pool behavior
   - Track memory usage

## Next Steps
1. Review and approve migration plan
2. Schedule production deployment
3. Execute migration
4. Monitor application performance
5. Document lessons learned

## Questions/Concerns
- Impact on existing queries using JSON fields
- Performance implications of JSONB vs TEXT
- Connection pool configuration with extended database
