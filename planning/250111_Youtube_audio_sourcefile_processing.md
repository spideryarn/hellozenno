# YouTube Audio Sourcefile Processing

## Goal Statement
Enable creating Sourcefiles from YouTube videos by downloading their audio tracks using yt-dlp. This will allow users to easily add audio content from YouTube videos (like interviews, news segments, etc.) as Sourcefiles for vocabulary extraction.

## Implementation Status

### Phase 1: Core Setup ✅
1. Add new dependencies ✅
   - Added yt-dlp to requirements.txt
   - Added minimal ffmpeg installation to Dockerfile
   - Updated installation docs

2. Add new sourcefile type ✅
   - Added 'youtube_audio' as valid sourcefile_type in config.py
   - Updated validation in models/sourcefile.py
   - Added relevant tests
   - Documented valid types

3. Create YouTube download functionality ✅
   - Created youtube_utils.py for yt-dlp integration
   - Supporting various YouTube URL formats:
     - Full: https://www.youtube.com/watch?v=VIDEO_ID
     - Short: https://youtu.be/VIDEO_ID
     - Mobile: https://m.youtube.com/watch?v=VIDEO_ID
   - Handling common errors (age restriction, unavailable videos, etc.)
   - Respecting MAX_AUDIO_SIZE_UPLOAD_ALLOWED (60MB) limit
   - Converting to MP3 format

### Phase 2: UI & Integration ✅
1. Add YouTube URL input ✅
   - Added form/button for URL submission in sourcefiles.jinja
   - Added to sourcedir view
   - Reusing existing audio player UI

2. Add backend processing ✅
   - Created endpoint for YouTube URL submission
   - Implemented download and process audio functionality
   - Fixed NOT NULL constraint issues with text fields
   - Storing metadata:
     ```python
     {
         "source": "youtube",
         "video_id": "...",
         "video_title": "...",
         "channel": "...",
         "upload_date": "...",
         "url": "...",
         "download_date": "..."
     }
     ```
   - Integrated with existing audio processing pipeline

### Phase 3: Testing & Documentation ✅
1. Add tests ✅
   - Added URL validation tests
   - Added download functionality tests
   - Added size limit tests
   - Added error case tests
   - Added mock YouTube responses for testing
   - Fixed test issues with file paths and mocks

2. Add documentation ✅
   - Updated README
   - Documented supported URL formats
   - Documented size limits
   - Documented error messages

## Current Limitations
1. Single videos only (no playlists)
2. No handling of age-restricted content
3. No video thumbnail storage
4. 60MB file size limit (from existing config)
5. MP3 format only

## Future Enhancements
1. Support for playlists
2. Handle age-restricted content
3. Store video thumbnails
4. Custom audio quality settings
5. Support for other audio formats
6. Progress bar for long downloads
7. Add download progress indicator in UI
8. Add video preview/metadata before download
9. Add batch download capability
10. Add option to specify start/end timestamps for partial video downloads

## Progress
- [x] Phase 1: Core Setup
- [x] Phase 2: UI & Integration
- [x] Phase 3: Testing & Documentation

## Implementation Plan

1. Fix sourcefile processing
   - Modify `sourcefile_processing.py` to handle "youtube_audio" type
   - Reuse existing audio processing pipeline since both types use MP3 files
   - Just treat "youtube_audio" same as "audio" for transcription

2. Clean up endpoints
   - Remove unused `/api/sourcedir/<target_language_code>/<sourcedir_slug>/add_from_youtube`
   - Keep `/<language_code>/<sourcedir_slug>/add_from_youtube`

3. Update UI
   - Change "Upload files" to "Upload image files"
   - Change "Add from YouTube" to "Pull YouTube audio"
   - Update button styles to be less "success" focused

4. Improve filename generation
   - Use video title directly without slugifying first
   - Add timestamp to avoid collisions
   - Keep .mp3 extension

Next Steps:
1. Start with sourcefile processing fix
2. Then clean up endpoints
3. Then update UI
4. Finally improve filename generation

## Recent Fixes
1. Fixed NOT NULL constraint issues with text fields
   - Both endpoints now properly initialize text_target and text_english with empty strings
   - This allows the initial file creation to succeed
   - Actual text content is populated later during processing with Whisper API

2. Fixed test issues
   - Improved mock setup for yt-dlp
   - Fixed file path handling in tests
   - Added better error handling and validation

3. Added better logging
   - Added debug logging for download process
   - Improved error messages for common failures
   - Added metadata logging for debugging

