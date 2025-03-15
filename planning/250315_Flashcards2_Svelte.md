# Flashcards2: Svelte-Based Language Learning Flashcards

## Goal, Context

Create a new Svelte-based flashcard system at `/<language_code>/flashcards2` that parallels the existing vanilla JS implementation, starting very simple, gradually adding in functionality, and enabling more complex functionality in the future. The current flashcards have a staged learning flow (audio → sentence → translation) that works well, but adding new features is difficult with the current architecture.

The new system should:
- Maintain the same core learning flow
- Be built with Svelte and TypeScript (rather than vanilla JavaScript) for better maintainability
- Separate business logic from UI for better testability
- Not disrupt the existing flashcard functionality during development

## Principles, Key Decisions

- **Component Structure**: Use a single Flashcard component that conditionally renders different content based on the current stage, rather than separate components per stage (though it may have sub-components)
- **Backend Separation**: Create new routes in `flashcard2_views.py` while reusing existing backend functionality (e.g. from `flashcard_views.py` and elsewhere) where possible
- **State Management**: Handle stage transitions and UI state in TypeScript
- **Progressive Enhancement**: Build in lots of small stages, starting with a minimal working implementation, and ending with working code at the end of each stage
- **Testability**: Write pure TypeScript functions for business logic that can be tested independently
- **Data Flow**: Continue sending one sentence at a time from the backend, enabling an infinite stream of flashcards
- **Simplicity**: If you see problems or a way to avoid complexity, make suggestions and ask the user
- **API-First**: Create a JSON API endpoint to allow the frontend to fetch data directly, enabling more flexible rendering
- **Testing Throughout**: Integrate basic smoke tests early in development and expand with each stage

## Useful

- `flashcard_views.py`
- `Sentence.svelte` - let's aim to reuse/share components with this where it makes sense (which might mean refactoring it - let's discuss)
- ...


## Architecture Overview

### Component Hierarchy
```
FlashcardApp (main container)
├── FlashcardStage (handles showing/hiding based on stage)
│   ├── AudioPlayer (plays sentence audio)
│   ├── SentenceDisplay (shows target language text)
│   └── TranslationDisplay (shows translation)
└── FlashcardNavigation (navigation controls)
    ├── PreviousButton
    ├── NextButton
    └── NewSentenceButton
```

### Data Flow
1. User navigates to `/<language_code>/flashcards2`
2. Flask renders template with initial sentence data
3. Svelte component mounts and initializes with data
4. User interacts with flashcard (changing stages, requesting new sentences)
5. For new sentences, AJAX request fetches next sentence data

### State Management
- `FlashcardState` TypeScript interface defines the complete state
- Pure functions handle state transitions between stages
- Component reactively updates based on state changes

## Actions

- [x] **Setup Project Structure**
  - [x] Create `flashcard2_views.py` with basic routes mirroring the current flashcard routes
  - [x] Create template file for the new flashcards2 page
  - [x] Create basic Svelte component structure in frontend
  - [x] Write basic smoke test to verify page loads and component mounts

- [x] **Basic Flashcard Display**
  - [x] Create JSON API endpoint to serve sentence data
  - [x] Create FlashcardApp Svelte component with minimal UI
  - [x] Implement TypeScript interfaces for flashcard data and state
  - [x] Create pure function for stage transitions
  - [x] Add basic styling to match existing flashcards
  - [x] Write unit test for stage transition functions

- [x] **Audio Playback**
  - [x] Implement AudioPlayer functionality within FlashcardApp
  - [x] Handle automatic audio playback on load
  - [x] Add controls for replaying audio
  - [x] Write test for audio player functionality

- [x] **Navigation and Stage Transitions**
  - [x] Implement FlashcardNavigation within FlashcardApp
  - [x] Add keyboard shortcuts (left/right/enter)
  - [x] Handle stage transitions with animations
  - [x] Ensure responsive design for mobile
  - [x] Test keyboard navigation functionality

- [x] **New Sentence Fetching**
  - [x] Enhance JSON API endpoint for fetching new sentences
  - [x] Implement client-side navigation for fetching sentences
  - [x] Add loading states and error handling
  - [x] Test sentence fetching and state updates

- [x] **Filtering by Sourcefile/Sourcedir**
  - [x] Add support for sourcefile/sourcedir URL parameters
  - [x] Update API endpoint to handle filtered sentences
  - [x] Add UI indication of the current filter
  - [x] Test filtering functionality

- [x] **Integration and End-to-end Testing**
  - [x] Write integration tests for complete flashcard functionality
  - [x] Add basic smoke test for page loading
  - [x] Create comparison with original flashcards for feature parity
  - [ ] Perform cross-browser and mobile testing (to be done with live users)
  - [ ] Document new system for future reference

## TypeScript Interfaces and Core Functions

### Key Interfaces
```typescript
interface SentenceData {
  id: number;
  slug: string;
  text: string;
  translation: string;
  lemma_words: string[];
  audio_url: string;
}

interface FlashcardState {
  stage: 1 | 2 | 3;  // 1: audio, 2: sentence, 3: translation
  sentence: SentenceData;
  isLoading: boolean;
  error: string | null;
  sourceFilter: {
    type: 'sourcefile' | 'sourcedir' | null;
    slug: string | null;
  };
}
```

### Core Functions
```typescript
// Pure function to advance stage
function advanceStage(state: FlashcardState): FlashcardState

// Pure function to go back a stage
function previousStage(state: FlashcardState): FlashcardState

// Function to fetch a new sentence
async function fetchNewSentence(
  languageCode: string, 
  sourceFilter?: {type: 'sourcefile' | 'sourcedir', slug: string}
): Promise<SentenceData>
```

## Flask Routes

```python
# Landing page for flashcards2
@flashcard2_views_bp.route("/<language_code>/flashcards2")

# View specific sentence
@flashcard2_views_bp.route("/<language_code>/flashcards2/sentence/<slug>")

# Redirect to random sentence
@flashcard2_views_bp.route("/<language_code>/flashcards2/random")

# JSON API endpoint for fetching sentence data
@flashcard2_views_bp.route("/<language_code>/flashcards2/api/sentence/<slug>", methods=["GET"])

# JSON API endpoint for fetching random sentence data
@flashcard2_views_bp.route("/<language_code>/flashcards2/api/random", methods=["GET"])
```

## Appendix

### Flashcard Stages

1. **Audio Stage**: 
   - Audio plays automatically
   - Sentence and translation are hidden
   - Left button replays audio
   - Right button shows sentence

2. **Sentence Stage**:
   - Sentence is visible
   - Translation remains hidden
   - Left button returns to audio stage
   - Right button shows translation

3. **Translation Stage**:
   - Both sentence and translation are visible
   - Left button returns to sentence stage
   - Right button is disabled

"Next" button is always available to fetch a new sentence (starting at stage 1).

## Implementation Summary

The Svelte-based flashcard system has been successfully implemented with the following features:

1. **Component Structure**:
   - `FlashcardApp.svelte` - Main component for displaying and interacting with flashcards
   - `FlashcardLanding.svelte` - Landing page component with start button and instructions
   - Used state management with TypeScript interfaces for strong typing

2. **API Endpoints**:
   - JSON API for fetching sentence data
   - Support for sourcefile/sourcedir filtering
   - Random sentence selection

3. **User Experience**:
   - Three-stage learning flow (audio → sentence → translation)
   - Keyboard shortcuts for navigation (left/right/enter)
   - Responsive design for mobile and desktop
   - Error handling for audio playback and data loading

4. **Testing**:
   - Unit tests for stage transition functions
   - Integration tests for component functionality
   - End-to-end tests for the complete flashcard flow

## Next Steps

1. **User Feedback**:
   - Gather feedback from users on the new flashcard interface
   - Compare user satisfaction between original and new implementation

2. **Feature Enhancements**:
   - Add progress tracking and statistics
   - Implement spaced repetition algorithm
   - Add ability to mark sentences as favorites

3. **Technical Improvements**:
   - Optimize backend performance for faster sentence fetching
   - Add offline support with service workers
   - Improve accessibility features
   
## Implementation Approach and Technical Details

### Component Architecture

The Flashcards2 system consists of two main components:

1. **FlashcardLanding.svelte**: Entry point showing introduction and start button
2. **FlashcardApp.svelte**: Main component handling the three-stage flashcard learning process

Both components integrate with Flask templates using the UMD module pattern, which provides several advantages:

- Reliable loading in both development and production environments
- No dependency on external module loading
- Compatible with all modern browsers without requiring polyfills

### Module Loading Strategy

We use a hybrid approach for component loading:

1. **Development**: Components are served through the Vite dev server
2. **Production**: Pre-built UMD bundles are served from static files

This is implemented via:
```jinja
{% if svelte_umd_mode is defined and svelte_umd_mode %}
<script src="{{ url_for('static', filename='build/js/hz-components.umd.js') }}"></script>
{% endif %}
```

### API Integration

The flashcard components interact with backend Flask routes through:

1. Direct API calls for dynamic data loading
2. Template-provided initial data for first render
3. URL-based navigation for changing sentences

### Implementation Challenges and Solutions

During implementation, we faced several challenges:

1. **Component Loading Issues**:
   - Problem: The Vite development server was returning TypeScript files with incorrect MIME types, causing errors in the browser.
   - Solution: We used UMD builds of the components and loaded them with script tags, avoiding the dynamic import issues.
   - Tradeoff: Slightly larger bundle size but more reliable cross-browser compatibility.

2. **Module Format Compatibility**:
   - Problem: The ES module format was causing issues with direct browser imports.
   - Solution: Generated both ES and UMD formats in the build process, using the UMD format for direct browser loading.
   - Note: This approach only affects the flashcards components, not other Svelte components.

3. **Svelte Integration**:
   - Problem: Svelte dependency was initially external, causing import errors.
   - Solution: Bundled Svelte into the UMD build to avoid external dependencies.
   - Impact: Increased bundle size but eliminated external dependencies.

4. **Keyboard Navigation**:
   - Problem: The ENTER keyboard shortcut only worked on the button element, not document-wide.
   - Solution: Added a document-level event listener that checks for the ENTER key press.
   - Implementation: Added code that prevents activation when input elements are focused.

These solutions ensure the flashcards work reliably regardless of environment or browser support for ES modules, with minimal impact on the rest of the application.

### Reuse and Component Sharing

There is potential for shared functionality between Sentence.svelte and the flashcard components:

1. **Potential Shared Elements**:
   - Audio playback functionality
   - Sentence and translation rendering
   - Styling and visual elements

2. **Reasons for Current Separation**:
   - Different user flows and purposes
   - Stage-based navigation in flashcards vs. static display in Sentence
   - Different state management requirements

3. **Future Refactoring Opportunities**:
   - Extract AudioPlayer into a separate component
   - Create shared utilities for sentence rendering
   - Establish common styling guidelines

