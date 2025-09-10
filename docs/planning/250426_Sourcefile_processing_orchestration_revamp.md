# Sourcefile Processing Orchestration Revamp

## Current Issues

1. **Auto-processing Limitation**: When first visiting a sourcefile, text extraction is automatically triggered, but translation doesn't follow in the same run.

2. **Processing Button Design**: The button becomes disabled during processing, limiting the ability to queue additional runs.

3. **Processing Flow Order**: The current implementation prioritizes completing all steps (including lemma metadata) before running more iterations of word extraction.

4. **Early Return in Step Determination**: The `determineSteps()` function returns early after adding the text extraction step, preventing other steps from being queued in the same iteration.

## Proposed Solutions

### 1. Fix Auto-Processing Flow

Remove the early return in `determineSteps()` to allow the queue to include all appropriate steps in a single iteration:

```typescript
// Current problematic code in determineSteps():
if ((this.sourcefileType === 'image' || this.sourcefileType === 'audio') && !status.has_text) {
  steps.push({
    type: 'text_extraction',
    // ...other properties
  });
  // This early return prevents translation from being queued in the same run
  return steps;
}
```

Replace with a more declarative approach that queues everything that can or will be able to run:

```typescript
// Improved approach:
const needsTextExtraction = 
  (this.sourcefileType === 'image' || this.sourcefileType === 'audio') && !status.has_text;

// 1. Add text extraction if needed
if (needsTextExtraction) {
  steps.push({
    type: 'text_extraction',
    // ...other properties
  });
}

// 2. Determine if text will be available after this run
const willHaveText = status.has_text || needsTextExtraction;

// 3. Queue translation if needed and text will be available
if (willHaveText && !status.has_translation) {
  steps.push({
    type: 'translation',
    // ...other properties
  });
}

// 4. Queue wordforms and phrases if text will be available
if (willHaveText) {
  steps.push({
    type: 'wordforms',
    // ...other properties
  });
  
  steps.push({
    type: 'phrases',
    // ...other properties
  });
}

// 5. Queue lemma metadata completion last
if (willHaveText && status.incomplete_lemmas_count > 0) {
  for (const lemmaInfo of status.incomplete_lemmas) {
    steps.push({
      type: 'lemma_metadata',
      // ...other properties
    });
  }
}
```

This maintains the proper processing order (text extraction → translation → wordforms/phrases → lemma metadata) while ensuring all steps that can run are queued in a single iteration.

### 2. Improve Multi-Click Processing

Modify how multiple button clicks are handled to prioritize word extraction:

1. Keep the current approach of incrementing `pendingRuns` with each click
2. Restructure the queue generation to prioritize multiple wordform runs before lemma metadata

Two implementation options:

#### Option A: Optimized for Simplicity

For multiple iterations, run repeated full passes but push lemma metadata to the end:

```typescript
// In processAll():
const normalSteps = [];
const lemmaMetadataSteps = [];

// Separate lemma metadata from other steps
stepsForThisIteration.forEach(step => {
  if (step.type === 'lemma_metadata') {
    lemmaMetadataSteps.push(step);
  } else {
    normalSteps.push(step);
  }
});

// Process normal steps for each iteration before lemma metadata
for (let i = 0; i < iterations; i++) {
  // Process all normal steps
  for (const step of normalSteps) {
    this.queue.enqueue(step);
  }
}

// Add lemma metadata steps last (only once)
for (const step of lemmaMetadataSteps) {
  this.queue.enqueue(step);
}
```

#### Option B: More Advanced (Future Enhancement)

Group steps by type and repeat only wordforms/phrases iterations before processing lemma metadata:

```typescript
// Group steps by type
const stepsByType = {
  text_extraction: [],
  translation: [],
  wordforms: [],
  phrases: [],
  lemma_metadata: []
};

stepsForThisIteration.forEach(step => {
  stepsByType[step.type].push(step);
});

// Process steps in the optimal order with repetition
// 1. Always process text_extraction and translation first (once)
stepsByType.text_extraction.forEach(step => this.queue.enqueue(step));
stepsByType.translation.forEach(step => this.queue.enqueue(step));

// 2. Process wordforms and phrases multiple times
for (let i = 0; i < iterations; i++) {
  stepsByType.wordforms.forEach(step => this.queue.enqueue(step));
  stepsByType.phrases.forEach(step => this.queue.enqueue(step));
}

// 3. Process lemma_metadata last (once)
stepsByType.lemma_metadata.forEach(step => this.queue.enqueue(step));
```

### 3. UX Improvements

1. **Enable Multiple Button Clicks**: Ensure the process button is not disabled during processing but instead shows a loading state while allowing additional clicks.

2. **Clear Progress Indication**: Update the UI to show:
   - Which iteration is currently running
   - Total pending iterations
   - Which step is currently processing

3. **Better Feedback**: Show real-time updates about which words are being processed or added.

## Implementation Plan

1. **Phase 1**: Fix the early return in `determineSteps()` to ensure auto-processing completes all steps in one run
   - This is the most critical change with the least complexity

2. **Phase 2**: Implement the simpler multi-click iteration model (Option A)
   - Ensures word extraction runs multiple times before lemma metadata
   - Maintains current UX with incremental improvements

3. **Phase 3** (Optional Future Enhancements):
   - Implement more advanced queuing logic (Option B)
   - Add parallel processing for lemma metadata
   - Enable infinite-loop-until-idle model as an alternative to manual iterations

## Additional Considerations

- Maintain proper error handling and progress reporting
- Ensure the UI remains responsive during processing
- Keep the current event dispatching for updating EnhancedText without page reloads
- Consider adding a "Process Everything" button that would run until no more processing is needed

## Implementation Status

Both Phase 1 and Phase 2 have been successfully implemented:

### Phase 1 ✅

The `determineSteps()` method in `processing-queue.ts` has been modified to:

- Remove the early return after adding the text extraction step
- Introduce a `needsTextExtraction` variable to track when text extraction is needed
- Add a `willHaveText` variable to determine if text will be available after the current run
- Queue all appropriate steps for processing in one run

The improved implementation ensures that when first visiting a sourcefile:
- Text extraction is immediately followed by translation in the same queue run
- Wordform extraction and phrase extraction also follow if text is or will be available
- All steps maintain the proper processing order

### Phase 2 ✅

The `processAll()` method has been completely redesigned to:

- Process steps in batches based on type rather than iterations
- Separate lemma metadata steps from normal steps
- Queue and process all normal steps for each iteration before any lemma metadata
- Provide better progress tracking and visual feedback

Additionally, the Process button in `SourcefileHeader.svelte` has been modified to:

- Remove the `disabled` attribute during processing
- Add a visual processing state with a shimmer animation effect
- Allow multiple clicks while processing is active
- Display a counter for queued processing runs

The multi-click processing now ensures that:
1. All text extraction and translation steps happen first (once)
2. All wordform/phrase extractions are repeated for each iteration/button click
3. Lemma metadata completion only happens once at the end

### Results

The implementation now provides a much smoother user experience:
- Automatic processing completes all necessary steps in one session
- Users can click the Process button multiple times to extract more vocabulary
- Visual feedback clearly shows progress, current step, and queued runs
- The interface remains responsive during processing

