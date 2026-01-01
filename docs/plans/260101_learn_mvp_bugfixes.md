# Plan: Learn MVP Bug Fixes

Created: 2026-01-01
Status: implementing
Complexity: medium
Confidence: 85%

## Task
Fix 8 bugs identified in the Learn from Sourcefile MVP through triple-review.

## Research Notes
- Sentence model has unique constraint on `(sentence, target_language_code)`
- Sourcefile has unique constraint on `(slug, sourcedir_id)`
- `generate_sentence()` uses `get_or_create` then unconditionally updates metadata
- Frontend `handleKeyDown` doesn't check `isEditable` for pre-practice mode

## Stages

### Stage 1: Backend validation fix (Bug #3)
- Status: pending
- Files: `backend/views/learn_api.py`
- Description: Add dict validation before accessing `.get()` on request body
- Rationale: Prevents 500 errors from malformed JSON

### Stage 2: Sourcedir context fix (Bug #1)
- Status: pending
- Files: `backend/views/learn_api.py`
- Description: Store and filter on `sourcedir_slug` in source_context
- Rationale: Prevents sentence cross-contamination between sourcedirs

### Stage 3: Sentence uniqueness migration (Bug #2)
- Status: pending
- Files: `backend/migrations/`, `backend/db_models.py`, `backend/utils/sentence_utils.py`
- Description: Add `source_key` column, change unique constraint to include it
- Rationale: Allows same sentence text with different sources without corruption

### Stage 4: Frontend UX fixes (Bugs #4, #5, #6, #8)
- Status: pending
- Files: `frontend/src/routes/.../learn/+page.svelte`
- Description: Fix keyboard handling, cleanup listeners, race conditions, preload leak
- Rationale: Improves UX and prevents memory leaks

### Stage 5: Audio variant uniqueness (Bug #7)
- Status: pending
- Files: `backend/utils/audio_utils.py`
- Description: Add conflict handling to prevent duplicate audio variants
- Rationale: Prevents wasted TTS calls and duplicate storage

## Design Decision: Bug #2 Approach

**Chosen: Option (a) - Make uniqueness include source context**

Implementation:
1. Add `source_key` column (nullable VARCHAR)
2. Change unique constraint to `(sentence, target_language_code, source_key)` using partial index
3. For "learn" provenance: `source_key = "{sourcedir_slug}/{sourcefile_slug}"`
4. For other provenances: `source_key = NULL`

Tradeoffs considered:
- (+) Clean separation - each source has its own sentence record
- (+) No data corruption when same text generated for different sources
- (-) Requires migration
- (-) Loses deduplication for "learn" sentences across sourcefiles (intentional for independent decks)
- (-) Two NULLs are distinct in PostgreSQL unique constraints, but we handle this with a partial index

Migration strategy:
- Existing sentences keep `source_key = NULL`
- New "learn" sentences get appropriate source_key
- Partial unique index: one on `(sentence, target_language_code) WHERE source_key IS NULL` for backwards compat, and one on `(sentence, target_language_code, source_key) WHERE source_key IS NOT NULL`

## Review History
- Initial review: 2026-01-01 - 8 bugs identified by GPT-5.2-high
- Post-implementation review: 2026-01-01 - GPT-5.2-high identified additional issues:
  1. Sentence lookups elsewhere need source_key in lookup - Fixed (vocab_llm_utils.py)
  2. Slug uniqueness also needs source_key partitioning - Fixed (updated migration)
  3. Frontend cleanup should abort in-flight requests - Fixed (onMount cleanup)
  4. Use source_key column instead of JSON extraction - Fixed (learn_api.py)
