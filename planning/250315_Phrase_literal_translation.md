# Add Literal Translation to Phrase Model

## Goal Statement
Add a "literal translation" field to the Phrase model that provides a word-for-word translation showing the grammatical structure of idiomatic phrases. This will help language learners understand both the idiomatic meaning (via the existing translations field) and the literal structure of phrases.

## Current Status
- Phrase model currently has translations field (JSONField) for idiomatic meanings
- No way to store or display literal, word-for-word translations
- No Svelte components specific to phrases found

## Changes Required

### Database Changes
1. Add `literal_translation` TextField to the Phrase model in db_models.py (nullable)
2. Update `to_dict()` method in the Phrase class to include the new field
3. Create a database migration (027_add_phrase_literal_translation.py)

### Frontend Changes
1. Update phrase.jinja template to display the literal translation
2. Place literal translation section after regular translations

### Backend Processing Changes
1. Update `extract_phrases_from_text` prompt template to include literal_translation in the JSON schema
2. Modify `process_phrases_from_text` in vocab_llm_utils.py to store literal_translation field
3. Add default empty value for literal_translation in phrase defaults

## Tasks
1. Update db_models.py:
   - Add literal_translation field
   - Update to_dict() method

2. Create migration:
   - Add column as nullable (existing rows won't have this data)

3. Update phrase.jinja:
   - Add section to display literal translation

4. Update prompt_templates.py:
   - Add literal_translation to JSON schema

5. Update vocab_llm_utils.py:
   - Update process_phrases_from_text
   - Add default value in phrase_defaults

6. Run migration:
   - Execute ./scripts/local/migrate.sh

7. Verify tests:
   - Check if tests/backend/conftest.py or other test fixtures need updating

## Acceptance Criteria
- Database model has literal_translation field
- Migration successfully adds column to database
- Template displays literal translation when available
- Extract phrases prompt includes literal_translation in schema
- Processing logic handles literal_translation field
- All tests pass after changes

## Notes
- Making field nullable since existing phrases won't have this data
- No Svelte components for phrases needed updating
- This enhancement will make it easier for language learners to understand phrase structure