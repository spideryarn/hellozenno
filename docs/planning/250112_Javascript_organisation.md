# JavaScript Organization Plan

## Goal Statement
Move JavaScript code from .jinja templates into separate .js files to improve maintainability and organization, while keeping functionality identical. Focus on one template at a time to ensure working code at each step.

## Current Status
All planned migrations completed! We've successfully moved JavaScript code from base.jinja, sourcedirs.jinja, sourcefile.jinja, sourcefiles.jinja, and sentence_flashcards.jinja to their respective .js files.

## Stage 1: Extract JavaScript to Separate Files

### Files to Process (in order)

DONE: base.jinja
- Move modal and Tippy.js initialization code to static/js/base.js
- Keep only script tag referencing new file
- Test modal functionality and word previews
- Acceptance: All tooltips and modals work as before

DONE: sourcedirs.jinja
- Created static/js/sourcedirs.js
- Moved modal and directory operations code
- Added target_language_code to window object
- Test directory creation and deletion
- Acceptance: All directory operations work as before

DONE: sourcefile.jinja
- Created static/js/sourcefile.js
- Moved file operations and audio functionality
- Test rename, delete, and audio generation
- Acceptance: All file operations and audio controls work as before

DONE: sourcefiles.jinja
- Created static/js/sourcefiles.js
- Moved file upload and YouTube integration code
- Added initialization code for file inputs and language selector
- Test file uploads and YouTube downloads
- Acceptance: All file operations work as before

DONE: sentence_flashcards.jinja
- Created static/js/sentence_flashcards.js
- Moved all flashcard and audio playback logic
- Added proper initialization and state management
- Test audio playback and keyboard shortcuts
- Acceptance: Flashcards work exactly as before, including keyboard shortcuts

### Implementation Notes
- Keep small inline event handlers (1-2 lines) in templates for now
- Add script tags at bottom of each template
- Keep all functionality identical - no refactoring yet
- Test thoroughly after each file migration

### Testing Process for Each File
1. Back up original template
2. Move JavaScript to new file
3. Add script tag to template
4. Test all functionality manually
5. Verify no console errors
6. If issues, compare with backup and fix

## Future Stages (Someday Maybe)
- Stage 2: Basic JavaScript improvements (modules, error handling)
- Stage 3: TypeScript migration
- Stage 4: Bundling and build process
- Stage 5: Testing infrastructure

## Summary of Changes
1. Improved code organization by separating JavaScript from templates
2. Made dependencies clearer through explicit window variables
3. Added proper initialization for each module
4. Maintained all existing functionality while improving maintainability
5. Set up foundation for future improvements (modules, TypeScript, etc.)
