# Audio Generation for Sourcefiles

## Goal Statement
Make MP3 audio generation optional for Sourcefile types that lack audio_data. Display audio controls in the `sourcefile.jinja` template when audio_data exists, otherwise show a "Generate audio" button that triggers MP3 generation using ElevenLabs. Store all audio in the audio_data field.

## Current Status
- DONE: Basic audio generation endpoint implemented
- DONE: UI for conditional audio player/generate button
- DONE: Loading indicator during generation
- DONE: Error handling for common cases
- DONE: Tests for audio generation endpoint
- DONE: Hide audio generation and practice buttons when no text content available

## Tasks

### Backend Implementation
DONE:
- Add `/api/sourcedir/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate_audio` endpoint
- Handle missing text content with 400 error
- Add error handling for API key and quota issues
- Implement cleanup of temporary files
- Add size validation for generated audio
- Store audio data in the Sourcefile.audio_data field

### Frontend Implementation
DONE:
- Add conditional rendering in `sourcefile.jinja`:
  - Show audio player if `sourcefile_entry.audio_data` exists
  - Show "Generate audio" button if no audio_data but has text content
  - Hide audio controls completely if no text content
- Add loading indicator with spinner during generation
- Handle API errors with user-friendly messages
- Refresh page after successful generation
- Hide "Practice with sentences" button when no text content available

### Testing
DONE:
- Add test_generate_sourcefile_audio with cases:
  - Successful generation
  - Missing text content
  - File not found
  - API errors
  - Size limit exceeded

### Bug Fixes
DONE:
- Fix field name in query (target_language_code → language_code)
- Fix client-side handling of 204 status code
- Improve error messages for common API issues
- Fix UI to not show audio/practice options when no text available

## Known Issues
- False positive linter errors for Peewee model fields (id, audio_data)
- These are expected and can be ignored as the fields do exist at runtime

## Next Steps
- Monitor for any issues with audio generation
- Consider adding:
  - Progress updates during generation
  - Cancellation option
  - Audio generation settings (voice, speed, etc)
  - Batch generation for multiple files
