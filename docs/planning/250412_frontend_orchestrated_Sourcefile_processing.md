# Frontend-Orchestrated Sourcefile Processing

## Goal and Context

This document outlines a plan to improve the sourcefile processing experience by implementing frontend orchestration for the various processing steps. The current synchronous implementation has limitations with timeout constraints and lacks visual feedback for users. The new approach will keep track of progress, allow for more resilience, and provide a better user experience.

## Goals

- Implement frontend orchestration for sourcefile processing
- Show visual feedback on processing progress
- Handle timeouts and errors gracefully
- Allow processing to continue after page refreshes
- Make the system more resilient

## Technologies

- `queue-typescript` for managing the processing queue
- Svelte stores for state management
- Flask API endpoints with individual processing steps
- SvelteKit for frontend implementation

## Implementation Stages

- [x] Stage: Basic Queue Implementation
  - [x] Install queue-typescript library
  - [x] Create a ProcessingQueue class in a new file: frontend/src/lib/processing-queue.ts
  - [x] Define the different processing steps (transcription, translation, wordforms, phrases)
  - [x] Implement basic queue initialization and processing
  - [x] Update SourcefileHeader.svelte to use the queue for the "Process" button

- [x] Stage: Progress UI
  - [x] Add a progress bar to show which step is currently being processed
  - [x] Create a Svelte store to track processing state
  - [x] Show status messages for the current processing step
  - [x] Ensure the UI is responsive during processing

- [x] Stage: Backend API Extensions
  - [x] Add a status endpoint to check what processing has been completed for a sourcefile
  - [x] Ensure each processing step has its own API endpoint
  - [x] Make sure all endpoints work synchronously and return appropriate status codes
  - [x] Make sure to restart Flask webserver after making any API route changes to update `routes.ts`

- [x] Stage: Error Handling and Resilience
  - [x] Implement error handling for each processing step
  - [x] Show error messages to the user

- [x] Stage: Enhanced Queue Features
  - [x] Add intelligent skipping of already completed steps
  - [x] Prioritize processing steps in order of importance (transcription → translation → extract wordforms → extract phrases)
  - [x] Show a detailed progress breakdown of completed and pending steps in the UI

- [x] Stage: API Modifications
  - [x] Update the backend to handle individual processing steps
  - [x] Ensure each step can run independently
  - [x] Add parameters to control the number of words/phrases to extract
  - [x] Optimize API responses for frontend consumption

- [ ] Stage: Improving user experience
  - [x] As a convenience for the user, automatically click the "Process" button when we open a Sourcefile page if a) there's no text_target, b) there's no translation, or c) There is a text_target with more than just "-" but no wordforms highlighted for the user to hover over - see ENHANCED_TEXT.md
  - [x] Add a counter so that the user can press the "Process" button multiple times, to tell it to run processing multiple times in sequence (and each time it'll get as many words/phrases as allowed in `backend/config.py`).
  - [x] After we have extracted tricky wordforms, we want to ideally update the hover-hyperlinks (see `create_interactive_word_data()`) so that the newly-extracted wordforms become new hover-hyperlinks. Ideally do this without having to reload the whole page. But I care more about keeping things simple than being over-clever.
  - [x] Complete the metadata for individual Lemmas. Added an API endpoint for processing individual lemmas and enhanced the queue to add each incomplete lemma as a separate processing step.
  - [x] Move more information to the progress bar as a tooltip (or visible if you click, e.g. on a mobile touch device). Added a detailed progress panel that shows comprehensive information about the current processing state, including step details, progress percentage, queued runs, and any errors.
  - [x] Don't flash up an annoying modal alert when you've finished processing. Instead, just display a nice message at the top when we've finished (perhaps with a tooltip with extra logging details). Replaced alert with an inline success notification that auto-dismisses after 5 seconds.
  - [x] Sometimes I'm seeing a duplicate key error message, e.g. "duplicate key value violates unique constraint "phrase_slug_language_code" DETAIL: Key (slug, target_language_code)=(sto-kato-kato, el) already exists.". Added special handling for duplicate key errors to log them as warnings but continue processing rather than treating them as fatal errors.
  - [x] I'm getting error message "Text must have been extracted first" - Fixed a race condition where the queue was trying to extract wordforms and phrases before text extraction was complete. Now wordforms and phrases are only queued when text is already available, and we refresh the queue after text extraction.
  - [x] After we have extracted more tricky wordforms, update the "Words (xxx)" and "Phrases (xxx)" counts in the tab bar above the text. Added code to update the local stats object with the latest counts when processing completes.
  - [ ] Should we move any of the existing functions in sourcefile_api.py over into sourcefile_api_processing.py?

- [ ] Stage: Parallel Processing
  - [ ] Implement parallel processing for independent steps (especially extracting the full lemma metadata)
  - [ ] Use Promise.all to manage multiple concurrent API calls
  - [ ] Add concurrency controls to prevent overwhelming the backend
  - [ ] Show parallel progress indicators in the UI

## Implementation Status

The implementation has been completed with the following major components:

1. ✅ Created a `processing-queue.ts` module with the `SourcefileProcessingQueue` class that uses the proper API routes
2. ✅ Implemented a Svelte store to track processing state with progress information
3. ✅ Updated `SourcefileHeader.svelte` to use the new queue with visual feedback
4. ✅ Implemented error handling for each processing step with user feedback
5. ✅ Added detailed progress UI with step-specific messages
6. ✅ Added queueing for multiple processing requests
7. ✅ Implemented dynamic updates to EnhancedText without page reloads
8. ✅ Added lemma metadata completion functionality
   - ✅ Created backend API endpoint for completing individual lemma metadata
   - ✅ Added function to find incomplete lemmas for a sourcefile
   - ✅ Enhanced the queue to process each lemma as a separate step

## Next Steps

All planned major features have been implemented successfully, including:

1. ✅ **Auto-Process Feature**: Auto-processing when a sourcefile is opened and meets certain criteria
   - ✅ Detect when a sourcefile needs processing (no text, no translation, or no highlighted words)
   - ✅ Add auto-processing logic that runs on component mount
   - ✅ Show a notification when auto-processing starts

2. ✅ **Multi-Processing Counter**: Multiple processing iterations for extracting more vocabulary
   - ✅ Added a counter UI to specify how many times to process a file sequentially
   - ✅ Modified the processing queue to handle multiple iterations
   - ✅ Added iteration progress tracking in the UI

3. ✅ **Enhanced Text Update**: Dynamic hover-hyperlink updates after processing
   - ✅ Added mechanism to fetch updated sourcefile data after processing
   - ✅ Created custom event system to notify components of data changes
   - ✅ Updated EnhancedText component to refresh tooltips without a page reload
   - ✅ Used Svelte's reactive declarations to watch for data changes

4. ✅ **Lemma Metadata Completion**: Individual processing of incomplete lemmas
   - ✅ Added function to identify incomplete lemmas for a sourcefile
   - ✅ Created API endpoint for processing individual lemma metadata
   - ✅ Added each lemma as a separate processing step in the queue
   - ✅ Enhanced status endpoint to report incomplete lemmas

The system now provides a complete, resilient solution for frontend-orchestrated Sourcefile processing with the following features:
- Step-by-step processing with detailed progress feedback
- Multiple processing iterations via queueing
- Real-time UI updates without page reloads
- Intelligent handling of incomplete lemmas
- Resilience against timeouts and errors

For future enhancements, consider adding:
- Parallel processing for lemma metadata completion
- Ordering lemma metadata completion by text appearance:
  - Modify `get_incomplete_lemmas_for_sourcefile()` to return lemmas ordered by their first appearance in the text
  - Join with `SourcefileWordform` and order by position/offset in the original text
  - Handle cases where a lemma has multiple wordforms in the text by using the first occurrence
  - This would prioritize completing metadata for words the user encounters first when reading

