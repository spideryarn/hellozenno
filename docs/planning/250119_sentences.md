# Migrate Sentence Management from GCS to PostgreSQL

## Goal Statement
Migrate sentence storage and management from Google Cloud Storage to our PostgreSQL database to align with our current architecture. This will enable better searching, management, and integration with other language learning features.

## Current Status
- Core database integration complete
- Audio data now stored in database as BlobField
- Basic test coverage added and passing
- Added new audio endpoint for serving audio from database
- Web interface updated to use new audio endpoint
- Added test coverage for audio serving endpoint

## Next Steps
1. Clean up:
   - Remove unused GCS code and imports
   - Update documentation
   - Remove unused audio file handling code

## Tasks

### Phase 1: Core Database Integration ✓
DONE:
1. Updated `sentence_utils.py` to use database instead of GCS:
   - Replaced `generate_sentence()` to save to DB
   - Updated `get_all_sentences()` to query DB
   - Updated `get_random_sentence()` to use DB query
   - Removed GCS-specific code and imports

2. ~~Create migration script to import existing sentences from GCS to DB~~
   - Skipped as no existing data needs to be migrated

3. Updated audio file handling:
   - Added `audio_data` BlobField to `Sentence` model
   - Created new `generate_sentence_audio()` function
   - Removed filesystem storage
   - Added audio serving endpoint

### Phase 2: API and Web Interface Updates ✓
DONE:
4. Updated Flask routes for sentence operations:
   - Added GET /api/{lang}/sentences/{id}/audio endpoint
   - Updated metadata to include sentence IDs
   - Updated web interface to use new endpoints

5. Updated web interface:
   - Modified audio playback to use new endpoint
   - Removed old filesystem-based audio handling
   - Added error handling for audio loading

### Phase 3: Testing and Cleanup
DONE:
6. Add API endpoint tests:
   - Added test_sentence_views.py
   - Added tests for audio serving endpoint
   - Added tests for error cases (missing audio, invalid IDs)
   - Added tests for wrong language code

TODO:
7. Clean up:
   - Remove unused GCS code and imports
   - Update documentation
   - Remove unused audio file handling code

## Completed Tasks History
DONE:
- Created `Sentence` model in database
- Added audio_data field to Sentence model
- Updated sentence_utils.py to use database
- Created new audio generation function
- Added audio serving endpoint
- Updated web interface
- Added basic test coverage
- Fixed test failures related to Sourcefile dependency
- Added comprehensive test coverage for audio serving endpoint

## Notes
- Audio data now stored directly in database as BlobField
- No migration needed as there was no existing data
- Audio generation now handled by dedicated function
- Consider adding compression for audio data if size becomes an issue
- Consider caching for frequently accessed audio files

## Testing Instructions
1. API Testing:
   - Run `pytest test_sentence_views.py` to test audio serving functionality
   - Tests cover:
     - Successful audio retrieval
     - Non-existent sentences
     - Missing audio data
     - Wrong language code

2. Browser Testing:
   - Navigate to sentence flashcards
   - Test audio playback for sentences
   - Verify error handling for missing audio
