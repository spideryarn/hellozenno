# Adding Audio Sourcefile Support

## Goal Statement
from db_models import Sourcefile


Enable creating Sourcefile from audio files (MP3 format) using OpenAI's Whisper API for speech-to-text transcription. This will allow users to upload audio content (like podcasts, lectures, or conversations) and have them automatically transcribed for vocabulary extraction, similar to how we handle images with OCR.

## Current Status
Phase 1 in progress - Core backend changes being implemented.

## Implementation Plan

### Phase 1: Core Backend Changes
DONE:
1. Create audio_utils.py
   - Added function to call OpenAI Whisper API directly
   - Added file validation and size checks
   - Support all languages from SUPPORTED_LANGUAGES
   - Preserved existing audio functionality

2. Update config.py
   - Added AUDIO_SOURCE_EXTENSIONS = {".mp3"}
   - Added MAX_AUDIO_SIZE_UPLOAD_ALLOWED (60MB for 60min MP3)
   - Added MAX_AUDIO_SIZE_FOR_STORAGE (same as upload size)
   - Updated SOURCE_EXTENSIONS to include audio

TODO:
3. Add "audio" as valid sourcefile_type
   - Update validation in models/sourcefile.py
   - Update relevant tests
   - Document valid types

4. Add audio file handling to sourcedir_views.py
   - Add audio file upload endpoint
   - Integrate with audio_utils.py
   - Store original audio file in Sourcefile.audio_data
   - Handle API errors gracefully

### Phase 2: UI Changes
TODO:
1. Add audio upload button
   - Support drag-and-drop
   - Show MP3 format requirement
   - Add file size indicator
   - Add language selector (matching SUPPORTED_LANGUAGES)

2. Add processing feedback
   - Show transcription progress
   - Handle errors gracefully
   - Provide retry options

### Phase 3: Testing & Polish
TODO:
1. Add comprehensive tests to test_sourcedir_views.py
   - Test audio file validation (format, size)
   - Test Whisper API integration
   - Test error cases
   - Test UI components
   - Add test audio fixtures

2. Documentation & Polish
   - Update README with audio support
   - Document API usage
   - Add usage examples
   - Final testing pass

## Decisions Made
1. Audio Format: MP3 only for initial implementation
2. File Storage: Store original audio in Sourcefile.audio_data
3. Language Support: All languages in SUPPORTED_LANGUAGES
4. Size Limits: Set to accommodate 60min medium-quality MP3 (60MB)
5. API Integration: Direct OpenAI Whisper API calls via audio_utils.py

## Progress
- Created audio_utils.py with transcribe_audio function that supports both file paths and file-like objects
- Added audio file validation and size limit checks
- Updated sourcefile_processing.py to handle audio files using BytesIO
- Modified sourcedir_views.py to support audio file uploads
- Updated templates/sourcefiles.jinja to add audio upload UI elements

## Next Steps
1. Test the audio upload functionality
2. Add error handling for transcription failures
3. Update the UI to show audio file status and playback controls
4. Add support for audio file deletion and renaming
5. Add progress indicators for long-running transcription tasks


