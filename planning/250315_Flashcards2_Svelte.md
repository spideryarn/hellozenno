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
  - [ ] Write basic smoke test to verify page loads and component mounts

- [ ] **Basic Flashcard Display**
  - [ ] Create JSON API endpoint to serve sentence data
  - [ ] Create FlashcardApp Svelte component with minimal UI
  - [ ] Implement TypeScript interfaces for flashcard data and state
  - [ ] Create pure function for stage transitions
  - [ ] Add basic styling to match existing flashcards
  - [ ] Write unit test for stage transition functions

- [ ] **Audio Playback**
  - [ ] Implement AudioPlayer Svelte component
  - [ ] Handle automatic audio playback on load
  - [ ] Add controls for replaying audio
  - [ ] Write test for audio player functionality

- [ ] **Navigation and Stage Transitions**
  - [ ] Implement FlashcardNavigation component
  - [ ] Add keyboard shortcuts (left/right/enter)
  - [ ] Handle stage transitions with animations
  - [ ] Ensure responsive design for mobile
  - [ ] Test keyboard navigation functionality

- [ ] **New Sentence Fetching**
  - [ ] Enhance JSON API endpoint for fetching new sentences
  - [ ] Implement client-side AJAX for fetching sentences
  - [ ] Add loading states and error handling
  - [ ] Test sentence fetching and state updates

- [ ] **Filtering by Sourcefile/Sourcedir**
  - [ ] Add support for sourcefile/sourcedir URL parameters
  - [ ] Update API endpoint to handle filtered sentences
  - [ ] Add UI indication of the current filter
  - [ ] Test filtering functionality

- [ ] **Integration and End-to-end Testing**
  - [ ] Write integration tests for complete flashcard functionality
  - [ ] Perform cross-browser and mobile testing
  - [ ] Document new system for future reference
  - [ ] Create comparison with original flashcards for feature parity

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

