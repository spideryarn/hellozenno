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

- `npm install queue-typescript` for managing the processing queue
- Svelte stores for state management
- Existing Flask API endpoints with some modifications
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
  - [ ] Make sure to restart Flask webserver after making any API route changes to update `routes.ts`

- [x] Stage: Error Handling and Resilience
  - [x] Implement error handling for each processing step
  - [x] Show error messages to the user

- [ ] Stage: Enhanced Queue Features
  - [x] Add intelligent skipping of already completed steps
  - [x] Prioritize processing steps in order of importance (transcription → translation → extract wordforms → extract phrases -> individual lemma full metadata)
  - [x] Show a detailed progress breakdown of completed and pending steps (maybe this is a tooltip on the progress bar to keep the UI tidy)

- [x] Stage: API Modifications
  - [x] Update the backend to handle individual processing steps
  - [x] Ensure each step can run independently
  - [x] Add parameters to control the number of words/phrases to extract
  - [x] Optimize API responses for frontend consumption

- [ ] Stage: Improving user experience
  - [ ] As a convenience for the user, automatically click the "Process" button when we open a Sourcefile page if a) there's no text_target, b) there's no translation, or c) There is a text_target with more than just "-" but no wordforms highlighted for the user to hover over - see ENHANCED_TEXT.md
  - [ ] Add a counter so that the user can press the "Process" button multiple times, to tell it to run processing multiple times in sequence (and each time it'll get as many words/phrases as allowed in `backend/config.py`). Note: completing individual Lemma metadata should happen as a final stage, after extracting tricky wordforms/phrases as many times as requested.
  - [ ] Complete the metadata for individual Lemmas. The `extract_tricky_words()` function only gets the most essential fields for the Lemmas corresponding to the Wordforms it extracts. So at the end of each processing run, we need to completely process each Lemma with `metadata_for_lemma_full()`. Ideally there'd be a way to determine en masse which Lemmas are complete (they have an `is_complete` field). see `backend/docs/MODELS.md` .
  
- [ ] Stage: Parallel Processing
  - [ ] Implement parallel processing for independent steps (especially extracting the full lemma metadata)
  - [ ] Use Promise.all to manage multiple concurrent API calls
  - [ ] Add concurrency controls to prevent overwhelming the backend
  - [ ] Show parallel progress indicators in the UI


## Detailed Implementation Plan for Initial Stages

### Stage: Basic Queue Implementation

1. First, install the queue-typescript library:

```
npm install queue-typescript --save
```

2. Create a new file frontend/src/lib/processing-queue.ts:

```typescript
import { Queue } from 'queue-typescript';
import { writable } from 'svelte/store';

// Define processing step types
export type ProcessingStep =
  | 'text_extraction'
  | 'translation'
  | 'wordforms'
  | 'phrases';

// Define a step with its API endpoint and parameters
export interface QueuedStep {
  type: ProcessingStep;
  apiEndpoint: string;
  params: Record<string, any>;
  description: string;
}

// Create a store for tracking progress
export const processingState = writable({
  isProcessing: false,
  currentStep: null as ProcessingStep | null,
  progress: 0,
  totalSteps: 0,
  error: null as string | null,
});

export class SourcefileProcessingQueue {
  private queue: Queue<QueuedStep>;
  private sourcefileData: {
    target_language_code: string;
    sourcedir_slug: string;
    sourcefile_slug: string;
  };

  constructor(target_language_code: string, sourcedir_slug: string, sourcefile_slug: string) {
    this.queue = new Queue<QueuedStep>();
    this.sourcefileData = {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    };
  }

  // Add the necessary steps based on what's needed
  public initializeQueue(sourcefile: any) {
    // Clear the existing queue
    this.queue = new Queue<QueuedStep>();

    // Check if text extraction is needed (for image or audio files)
    if (!sourcefile.text_target && (sourcefile.has_image || sourcefile.has_audio)) {
      this.queue.enqueue({
        type: 'text_extraction',
        apiEndpoint: `/api/lang/sourcefile/${this.sourcefileData.target_language_code}/${this.sourcefileData.sourcedir_slug}/${this.sourcefileData.sourcefile_slug}/extract_text`,
        params: {},
        description: 'Extracting text'
      });
    }

    // Check if translation is needed
    if (!sourcefile.text_english && sourcefile.text_target) {
      this.queue.enqueue({
        type: 'translation',
        apiEndpoint: `/api/lang/sourcefile/${this.sourcefileData.target_language_code}/${this.sourcefileData.sourcedir_slug}/${this.sourcefileData.sourcefile_slug}/translate`,
        params: {},
        description: 'Translating text'
      });
    }

    // Always add wordforms and phrases processing
    this.queue.enqueue({
      type: 'wordforms',
      apiEndpoint: `/api/lang/sourcefile/${this.sourcefileData.target_language_code}/${this.sourcefileData.sourcedir_slug}/${this.sourcefileData.sourcefile_slug}/process_wordforms`,
      params: {},
      description: 'Extracting vocabulary'
    });

    this.queue.enqueue({
      type: 'phrases',
      apiEndpoint: `/api/lang/sourcefile/${this.sourcefileData.target_language_code}/${this.sourcefileData.sourcedir_slug}/${this.sourcefileData.sourcefile_slug}/process_phrases`,
      params: {},
      description: 'Extracting phrases'
    });

    // Update the store with the total steps
    processingState.update(state => ({
      ...state,
      totalSteps: this.queue.length,
      progress: 0
    }));

    return this.queue.length > 0;
  }

  // Process the next step in the queue
  public async processNextStep() {
    if (this.queue.length === 0) {
      processingState.update(state => ({
        ...state,
        isProcessing: false,
        currentStep: null,
        progress: state.totalSteps,
      }));
      return false;
    }

    const step = this.queue.dequeue();

    processingState.update(state => ({
      ...state,
      isProcessing: true,
      currentStep: step.type,
      error: null,
    }));

    try {
      const response = await fetch(step.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(step.params),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `Failed to process ${step.type}`);
      }

      processingState.update(state => ({
        ...state,
        progress: state.totalSteps - this.queue.length,
      }));

      return true;
    } catch (error) {
      processingState.update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
      return false;
    }
  }

  // Start processing the entire queue
  public async processAll() {
    processingState.update(state => ({
      ...state,
      isProcessing: true,
      progress: 0,
      error: null,
    }));

    while (this.queue.length > 0) {
      const success = await this.processNextStep();
      if (!success) {
        break;
      }
    }

    processingState.update(state => ({
      ...state,
      isProcessing: this.queue.length > 0,
    }));

    return this.queue.length === 0;
  }
}
```

3. Update the SourcefileHeader.svelte component to use the new queue:

```svelte
<script lang="ts">
  // Existing imports...
  import { SourcefileProcessingQueue, processingState } from '$lib/processing-queue';

  // Existing props...

  // Create a reactive variable for the processing queue
  $: processingQueue = new SourcefileProcessingQueue(
    target_language_code,
    sourcedir_slug,
    sourcefile_slug
  );

  // Subscribe to the processing state
  const processingProgress = processingState;

  async function processSourcefile() {
    if ($processingProgress.isProcessing) return;

    try {
      // Initialize the queue based on what needs to be processed
      const hasSteps = processingQueue.initializeQueue(sourcefile);

      if (!hasSteps) {
        // Nothing to process
        alert('No processing steps needed.');
        return;
      }

      // Start processing
      await processingQueue.processAll();

      // When done, reload the page to see the processed results
      window.location.reload();
    } catch (error) {
      console.error('Error processing file:', error);
      processingError = error instanceof Error ? error.message : 'Unknown error';
    }
  }
</script>

<!-- Update the process button UI to show progress -->
<div class="section process-section">
  <button on:click={processSourcefile} class="button" disabled={$processingProgress.isProcessing}>
    {#if $processingProgress.isProcessing}
      {$processingProgress.currentStep ? `${$processingProgress.description || 'Processing'}...
(${$processingProgress.progress}/${$processingProgress.totalSteps})` : 'Processing...'}
    {:else}
      Process this text
    {/if}
  </button>
  {#if $processingProgress.error}
    <span class="error-message">{$processingProgress.error}</span>
  {/if}
</div>

<!-- Add a progress bar if processing -->
{#if $processingProgress.isProcessing && $processingProgress.totalSteps > 0}
  <div class="progress-container">
    <div class="progress-bar" style="width: {($processingProgress.progress / $processingProgress.totalSteps) * 100}%"></div>
  </div>
{/if}

<style>
  /* Add styles for the progress bar */
  .progress-container {
    width: 100%;
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    margin-top: 8px;
    overflow: hidden;
  }

  .progress-bar {
    height: 100%;
    background-color: #4CAD53;
    transition: width 0.3s ease;
  }
</style>
```

### Stage: Backend API Modifications

We need to add several new endpoints to the backend to support the individual processing steps. Here's what we'd need to add to
/backend/views/sourcefile_api.py:

```python
@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/extract_text",
    methods=["POST"],
)
def extract_text_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Extract text from a sourcefile (image or audio)."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Extract text
        sourcefile_entry = ensure_text_extracted(sourcefile_entry)

        return jsonify({
            "success": True,
            "has_text": bool(sourcefile_entry.text_target),
        })

    except Exception as e:
        current_app.logger.error(f"Error extracting text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/translate",
    methods=["POST"],
)
def translate_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Translate the text of a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Ensure we have text to translate
        if not sourcefile_entry.text_target:
            return jsonify({"success": False, "error": "No text to translate"}), 400

        # Translate the text
        sourcefile_entry = ensure_translation(sourcefile_entry)

        return jsonify({
            "success": True,
            "has_translation": bool(sourcefile_entry.text_english),
        })

    except Exception as e:
        current_app.logger.error(f"Error translating text: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_wordforms",
    methods=["POST"],
)
def process_wordforms_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process wordforms for a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get processing parameters from request or use defaults
        data = request.get_json() or {}

        max_new_words = int(data.get("max_new_words", DEFAULT_MAX_NEW_WORDS_FOR_PROCESSED_SOURCEFILE))
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)

        # Process wordforms
        sourcefile_entry, _ = ensure_tricky_wordforms(
            sourcefile_entry,
            language_level=language_level,
            max_new_words=max_new_words,
        )

        return jsonify({
            "success": True,
            "params": {
                "max_new_words": max_new_words,
                "language_level": language_level,
            },
        })

    except Exception as e:
        current_app.logger.error(f"Error processing wordforms: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process_phrases",
    methods=["POST"],
)
def process_phrases_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process phrases for a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get processing parameters from request or use defaults
        data = request.get_json() or {}

        max_new_phrases = int(data.get("max_new_phrases", DEFAULT_MAX_NEW_PHRASES_FOR_PROCESSED_SOURCEFILE))
        language_level = data.get("language_level", DEFAULT_LANGUAGE_LEVEL)

        # Process phrases
        sourcefile_entry, _ = ensure_tricky_phrases(
            sourcefile_entry,
            language_level=language_level,
            max_new_phrases=max_new_phrases,
        )

        return jsonify({
            "success": True,
            "params": {
                "max_new_phrases": max_new_phrases,
                "language_level": language_level,
            },
        })

    except Exception as e:
        current_app.logger.error(f"Error processing phrases: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@sourcefile_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/status",
    methods=["GET"],
)
def sourcefile_status_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Get the processing status of a sourcefile."""
    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Check what processing has been completed
        status = {
            "has_text": bool(sourcefile_entry.text_target),
            "has_translation": bool(sourcefile_entry.text_english),
            "wordforms_count": SourcefileWordform.select().where(
                SourcefileWordform.sourcefile == sourcefile_entry
            ).count(),
            "phrases_count": SourcefilePhrase.select().where(
                SourcefilePhrase.sourcefile == sourcefile_entry
            ).count(),
        }

        return jsonify({
            "success": True,
            "status": status,
        })

    except Exception as e:
        current_app.logger.error(f"Error getting sourcefile status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
```

### Stage: Enhanced Progress UI

For a better user experience, we can enhance the UI to show more detailed progress:

```svelte
<!-- In SourcefileHeader.svelte -->

<!-- Add a more detailed progress UI -->
{#if $processingProgress.isProcessing}
  <div class="processing-status">
    <div class="progress-container">
      <div class="progress-bar" style="width: {($processingProgress.progress / $processingProgress.totalSteps) * 100}%"></div>
    </div>
    <div class="progress-text">
      {#if $processingProgress.currentStep === 'text_extraction'}
        <span>Transcribing content... ({$processingProgress.progress}/{$processingProgress.totalSteps})</span>
      {:else if $processingProgress.currentStep === 'translation'}
        <span>Translating to English... ({$processingProgress.progress}/{$processingProgress.totalSteps})</span>
      {:else if $processingProgress.currentStep === 'wordforms'}
        <span>Extracting vocabulary... ({$processingProgress.progress}/{$processingProgress.totalSteps})</span>
      {:else if $processingProgress.currentStep === 'phrases'}
        <span>Finding useful phrases... ({$processingProgress.progress}/{$processingProgress.totalSteps})</span>
      {:else}
        <span>Processing... ({$processingProgress.progress}/{$processingProgress.totalSteps})</span>
      {/if}
    </div>
  </div>
{/if}

<style>
  .processing-status {
    margin-top: 1rem;
    padding: 0.5rem;
    background-color: rgba(76, 173, 83, 0.1);
    border-radius: 4px;
  }

  .progress-text {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #4CAD53;
  }
</style>
```

## Implementation Status

The initial implementation has been completed:

1. ✅ Created a `processing-queue.ts` module with the `SourcefileProcessingQueue` class
2. ✅ Implemented a Svelte store to track processing state
3. ✅ Updated `SourcefileHeader.svelte` to use the new queue
4. ✅ Added backend API endpoints for individual processing steps
5. ✅ Added progress UI with detailed step information
6. ✅ Implemented error handling for each processing step

## Next Steps

Future enhancements should focus on:

1. Adding the counter functionality to track how many times the user has processed a file
2. Implementing localStorage persistence for queue state (to resume after page refresh)
3. Adding parallel processing for independent steps (especially lemma metadata generation)
4. Adding user preferences for processing behavior (like controlling max words/phrases count)
5. Implementing an option to retry specific failed steps

This modular approach has allowed us to implement a basic version and will enable us to progressively enhance it with more features as needed.

