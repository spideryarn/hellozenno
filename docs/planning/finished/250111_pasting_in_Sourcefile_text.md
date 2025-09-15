# Adding Text-Based Sourcefiles

## Goal Statement
Enable creating Sourcefiles by pasting text directly, rather than requiring an image upload. This will make it easier to add content from text sources and provide a simpler alternative to image uploads.

## Current Status
Phase 3 complete - Refactored processing logic and added comprehensive tests. Moving to Phase 4: Documentation & Final Polish.

## Recent Changes
1. Refactored sourcefile processing into a cleaner pipeline:
   - Single entry point `process_sourcefile_content`
   - Clear stages: get text -> translate -> extract vocabulary
   - New `get_text_from_sourcefile` function to handle different types
   - Removed redundant `process_image_file` function
   - Simpler testing with focused mocks
2. Maintained backward compatibility while simplifying code structure
3. Added support for future sourcefile types (audio, video, etc.)
4. All tests passing with minimal changes needed

## Implementation Plan

### Phase 1: Core Backend Changes ✓
DONE:
1. Add sourcefile_type field to Sourcefile model
   - Added required string field (no default value)
   - Using "image" and "text" as valid types
   - Created migration 011_add_sourcefile_type.py:
     a. Added nullable column
     b. Filled existing rows with "image"
     c. Made column required (NOT NULL)
   - Updated all tests to include sourcefile_type
   - Updated upload endpoint to set type="image" while preserving original functionality

2. Add create_from_text endpoint in sourcedir_views.py
   - Added new endpoint: POST /api/sourcedir/<target_language_code>/<sourcedir_slug>/create_from_text
   - Handles parameters: 
     * title (used as filename)
     * text_target (the content)
   - Sets sourcefile_type = "text"
   - Returns filename and slug
   - Added focused test in test_sourcedir_views.py

3. Update tests
   - Added test_create_sourcefile_from_text to test_sourcedir_views.py
   - Tested title/text validation
   - Tested error cases (empty text, invalid title)
   - Tested type field is set correctly
   - Verified existing image upload tests still pass

### Phase 2: UI Changes ✓
DONE:
1. Add "Create from Text" button in sourcefiles.jinja
   - Added next to upload buttons
   - Matches existing button styling
   - Mobile-friendly layout

2. Add modal dialog for text input
   - Reused modal styling from rename functionality
   - Added two fields:
     * Title input (becomes filename)
     * Text content textarea
   - Plain text only for v1
   - Submit/Cancel buttons
   - Responsive design for mobile

3. Add JavaScript to handle text submission
   - Added function to show/hide modal
   - Added function to submit to new API endpoint
   - Added error handling and user feedback
   - Added page reload on success

### Phase 3: Testing & Polish ✓
DONE:
1. Manual testing
   - Tested full flow end-to-end
   - Tested with various text lengths
   - Tested with non-ASCII text
   - Tested error cases:
     * Empty title/text
     * Duplicate filenames
     * Special characters in title
   - Verified image upload still works correctly

2. Code Refactoring
   - Moved processing logic to dedicated helper function process_sourcefile_content
   - Simplified view function to focus on routing and database operations
   - Added comprehensive tests for both view and helper functions
   - Improved error handling and validation
   - Maintained backward compatibility with existing functionality

IN PROGRESS:
### Phase 4: Documentation & Final Polish
1. Documentation
   - Update README with new functionality
   - Add comments explaining new code
   - Document valid sourcefile_type values
   - Add examples of text-based Sourcefile creation
   - Document processing helper function

2. Final Polish
   - Review error messages for clarity
   - Verify all edge cases are handled
   - Final pass of manual testing
   - Code cleanup and organization

## Future Improvements (v2+)
- Rich text formatting support
- Automatic title suggestion from text content
- Language detection/validation
- Support for pasting formatted text (e.g. from Word)
- Preview of text before submission
- Side-by-side target/English text input
- Support for multiple text formats (markdown, html, etc)
- Automatic text cleanup (remove extra whitespace, normalize quotes)

## Acceptance Criteria
1. ✓ Users can create a new Sourcefile by pasting text with a title
2. ✓ Text-based Sourcefiles work with all existing functionality (processing, viewing, editing)
3. ✓ UI is simple and intuitive
4. ✓ Sourcefile type is clearly indicated in the UI
5. ✓ All tests pass
6. Code is well-documented
7. ✓ Error cases are handled gracefully
8. ✓ Existing image upload functionality works unchanged
9. ✓ Processing logic is clean and maintainable
10. ✓ Test coverage is comprehensive

## Notes
- Keep v1 simple - just the core functionality
- Reuse existing code and patterns where possible
- Focus on maintainability and extensibility for future improvements
- Follow migration best practices from MIGRATIONS.md
- Preserve existing functionality while adding new features
- Keep changes minimal and focused

## Recent Changes
1. Refactored processing logic into process_sourcefile_content helper function
2. Updated test_process_sourcefile to use new processing helper
3. Improved error handling in both view and helper functions
4. Maintained backward compatibility while simplifying code structure
5. Added comprehensive tests for both image and text processing
