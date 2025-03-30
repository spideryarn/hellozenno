# Port to SvelteKit

## Goal

We built a Flask/Jinja + Svelte app called "Hello Zenno" in `views/` and `static/`.

We're going to keep Flask for an API (e.g., `views/*_api.py`), but port all user-facing parts to SvelteKit.

## Principles

- Simple, minimal, use robust best practices
- Better to fail with a loud error than run silently with wrong behavior
- SvelteKit for user-facing, Python for API
- Backend database on Supabase, Python serverless hosting on Vercel
- Don't optimize for performance
- Break down into lots of small stages that work on a small slice of functionality, ending each stage with working code
- Start very basic, gradually layer in complexity
- Avoid hacks, fallbacks, and bandaids
- Don't worry about backend compatibility
- Keep the code concise
- Discuss uncertainties rather than guessing
- Don't number or add headings to the Actions stages, so it's easy to reorder them

## Decisions from User

- Development: Run Flask (port 3000) and Vite (port 5173) servers separately
- State management: Not too complex yet, but will integrate Supabase frontend library later
- Styling: Using Bootstrap 5.3.2 with a custom dark theme for consistent styling
- Auth: Supabase will handle auth
- Migration priority: Start with languages.jinja, then Sentence.svelte
- TypeScript: Use typing fairly strictly for IDE benefits, not purist
- SvelteKit features: Yes to server-side rendering

## Plan: Small Stages

Project Setup & Configuration
- [x] Create SvelteKit project (done: renamed to `sveltekit_hz`)
- [x] Configure SvelteKit routes and basic layout structure
- [x] Setup basic API connection to Flask backend
- [x] Test a simple API call from SvelteKit to Flask

Languages Page - Basic
- [x] Create minimal Languages route
- [x] Fetch languages data from API
- [x] Display basic languages list without styling
- [x] Test route works and displays data correctly

Languages Page - Styling
- [x] Add CSS similar to original languages.jinja
- [x] Implement responsive grid layout
- [x] Ensure links work correctly 

API Integration
- [x] Refine SvelteKit-to-Flask API interactions
- [x] Create language name lookup API endpoint
- [x] Use backend API for translations and language information

Docs
- [x] Write up `sveltekit_hz/README.md` in detail

Bootstrap Styling Implementation
- [x] Setup Bootstrap 5.3.2 with local files (not CDN)
- [x] Create custom dark theme with variables in theme-variables.css
- [x] Implement reusable component styles in components.css  
- [x] Update layouts and pages to use Bootstrap classes
- [x] Create Card and SourceItem reusable components
- [x] Refactor Sentence component to use Bootstrap

Component Library
- [x] Create reusable UI components
  - [x] Card.svelte for language cards
  - [x] SourceItem.svelte for source listings
  - [x] Update Sentence.svelte to use Bootstrap
- [x] Set up consistent component exports in $lib/index.ts
- [x] Document component usage in README

Create any missing Flask APIs
For each Jinja view, we'll need to create a corresponding API that we can call from SvelteKit, e.g. if we have `views/blah_views.py blah_vw()`, we'll need to create/update `views/blah_api.py` and add `blah_api()`, we might need to update the Blueprints with the new `blah_api`. We want to reuse code, so we'll probably need to abstract out what's common to the Jinja-view and API functions into a `blah_utils.py blah_core()` that they can both call. see `views/languages_views.py get_languages_api()` as an example.
Tail the files in `logs/` to see the output of the Sveltekit and Flask development servers
- [x] Write a list of all the current Flask Jinja views in an Appendix at the bottom, with checkboxes next to each
- [ ] Create all the new API views, stopping to discuss after each one.
- [ ] Update the Svelte frontend as appropriate to use the new API (e.g. add a new route, or a new button, or whatever)
- [ ] Test the new functionality, e.g. with curl or Playwright MCP, or ask the user 

#### API Creation Todo List
Create the following missing API endpoints that correspond to existing view functions:

**System API**
- [ ] Create `health_check_api()` in `system_api.py` (from `health_check_vw()`)
- [ ] Create `route_test_api()` in `system_api.py` (from `route_test_vw()`)

**Search API**
- [ ] Create `search_landing_api()` in `search_api.py` (from `search_landing_vw()`)
- [ ] Create `search_word_api()` in `search_api.py` (from `search_word_vw()`)

**Language Resources API**
- [ ] Create `wordforms_list_api()` in `wordform_api.py` (from `wordforms_list_vw()`)
- [ ] Create `get_wordform_metadata_api()` in `wordform_api.py` (from `get_wordform_metadata_vw()`)
- [ ] Create `delete_wordform_api()` in `wordform_api.py` (from `delete_wordform_vw()`)
- [x] Create `lemmas_list_api()` in `lemma_api.py` (from `lemmas_list_vw()`)
- [x] Create `phrases_list_api()` in `phrase_api.py` (from `phrases_list_vw()`)
- [ ] Create `get_phrase_metadata_api()` in `phrase_api.py` (from `get_phrase_metadata_vw()`)
- [ ] Create `delete_phrase_api()` in `phrase_api.py` (from `delete_phrase_vw()`)
- [x] Create `sentences_list_api()` in `sentence_api.py` (from `sentences_list_vw()`)

**Source Files API**
- [ ] Create `sourcefiles_for_sourcedir_api()` in `sourcedir_api.py` (from `sourcefiles_for_sourcedir_vw()`)
- [ ] Create `inspect_sourcefile_api()` in `sourcefile_api.py` (from `inspect_sourcefile_vw()`)
- [ ] Create `inspect_sourcefile_text_api()` in `sourcefile_api.py` (from `inspect_sourcefile_text_vw()`)
- [ ] Create `inspect_sourcefile_words_api()` in `sourcefile_api.py` (from `inspect_sourcefile_words_vw()`)
- [ ] Create `inspect_sourcefile_phrases_api()` in `sourcefile_api.py` (from `inspect_sourcefile_phrases_vw()`)
- [ ] Create `view_sourcefile_api()` in `sourcefile_api.py` (from `view_sourcefile_vw()`)
- [ ] Create `download_sourcefile_api()` in `sourcefile_api.py` (from `download_sourcefile_vw()`)
- [ ] Create `process_sourcefile_api()` in `sourcefile_api.py` (from `process_sourcefile_vw()`)
- [ ] Create `play_sourcefile_audio_api()` in `sourcefile_api.py` (from `play_sourcefile_audio_vw()`)
- [ ] Create `sourcefile_sentences_api()` in `sourcefile_api.py` (from `sourcefile_sentences_vw()`)
- [ ] Create `next_sourcefile_api()` in `sourcefile_api.py` (from `next_sourcefile_vw()`)
- [ ] Create `prev_sourcefile_api()` in `sourcefile_api.py` (from `prev_sourcefile_vw()`)

**Auth/User API**
- [ ] Create `auth_page_api()` in `auth_api.py` (from `auth_page_vw()`)
- [ ] Create `protected_page_api()` in `auth_api.py` (from `protected_page_vw()`)
- [ ] Create `profile_page_api()` in `auth_api.py` (from `profile_page_vw()`)

**Flashcard API**
- [ ] Create `flashcard_landing_api()` in `flashcard_api.py` (from `flashcard_landing_vw()`)

Sentence Component - Basic Structure
- [x] Create Sentence component with minimal functionality
- [x] Define TypeScript interfaces for sentence data
- [x] Set up basic layout without complex features

Sentence Component - Enhanced Features
- [x] Implement word highlighting
- [x] Add translations display
- [x] Set up metadata section

Sentence Component - Audio Integration
- [x] Add audio player functionality
- [x] Implement playback controls
- [ ] Add audio generation capability

Authentication Integration
- [ ] Discuss Supabase auth approach
- [ ] Plan auth integration in SvelteKit
- [ ] Implement basic authentication flow

Later Stages (To Discuss)
- [ ] Enhance styling and user experience - discuss CSS framework decision (Bootstrap vs alternatives)
- [ ] Set up deployment configuration
- [ ] Discuss form handling approach in SvelteKit
- [ ] Supabase realtime updates integration
- [ ] Deployment strategy for Vercel
- [ ] Implement authentication

## Design System Guidelines

### CSS Structure

Our CSS is organized into modular files for better maintainability:

```
static/css/
├── base.css               # Main CSS file that imports others
├── theme-variables.css    # Theme variables (colors, fonts, etc.)
├── theme.css              # Theme-specific styling
├── components.css         # Component-specific styles
└── extern/
    └── bootstrap/
        └── bootstrap.min.css  # Bootstrap core CSS
```

### Color Palette

- **Background**: Near-black (`#121212`)
- **Text**: Near-white (`#e9e9e9`)
- **Primary**: Bright green (`#4CAD53`) - for highlights, buttons, active elements
- **Secondary**: Complementary orange (`#D97A27`) - for accents, secondary actions

### Typography

- **Primary Font**: Georgia
- **Foreign Language Text**: Times New Roman, italic
- **Monospace**: Menlo, Monaco, Courier New (for code and metadata)

### Component Naming

We use the prefix `hz-` for all custom component classes:
- `.hz-language-item`: For language cards
- `.hz-foreign-text`: For foreign language text
- `.hz-source-item`: For source items

### How to Create New Pages

1. Use Bootstrap utility classes for layout
2. Import our reusable components from `$lib`
3. Apply custom classes from components.css as needed
4. Maintain the dark theme aesthetics

## Actions & Progress

### Completed
- [x] Create SvelteKit project
- [x] Set up basic layout and routing structure
- [x] Implement the languages page with server-side data fetching
- [x] Create placeholder for language/[language_code]/sources route
- [x] Connect Flask API with SvelteKit frontend
- [x] Create sentence component skeleton
- [x] Successfully implement and test Sentence component
- [x] Fixed API routes for better coordination between Flask and SvelteKit
- [x] Enhanced backend APIs by adding language name lookup endpoint
- [x] Improved SvelteKit server-side rendering with proper fetch handling
- [x] Implemented Bootstrap with custom dark theme
- [x] Created reusable component library
- [x] Updated existing pages to use new styling

### In Progress
- [ ] Enhance sentence component with more features
- [ ] Implement remaining language-specific routes

## Questions

- Best practice for API route structure between SvelteKit and Flask?
- How to handle environment configuration across both services?
- Deployment strategy details for Vercel?

## Sourcefile Page Implementation

### Stages for Implementation

1. **API Backend**
   - [ ] Create `inspect_sourcefile_api()` in `views/sourcefile_api.py`
   - [ ] Create `inspect_sourcefile_text_api()` in `views/sourcefile_api.py`
   - [ ] Test API endpoints with curl or similar tool

2. **SvelteKit Basic Structure**
   - [ ] Create route structure for `/language/[language_code]/source/[sourcefile_slug]`
   - [ ] Implement server-side data fetching in `+page.server.ts`
   - [ ] Create basic layout for the page in `+page.svelte`

3. **Component Breakdown**
   - [ ] Create `SourcefileHeader` component
     - [ ] Implement file metadata display
     - [ ] Add navigation buttons
     - [ ] Include sourcefile tabs
   - [ ] Create `SourcefileText` component
     - [ ] Display the text content
     - [ ] Add collapsible translation section

4. **Functionality**
   - [ ] Implement tab navigation
   - [ ] Hook up process button
   - [ ] Set up previous/next navigation
   - [ ] Add description editing functionality

5. **Later Enhancements**
   - [ ] Implement enhanced text with interactive word links
   - [ ] Add styling to match the original design
   - [ ] Create words and phrases tabs with full functionality

6. **SvelteKit Structure**:

We're approaching the SvelteKit implementation with a component-based architecture:

```
/routes/language/[language_code]/source/[sourcefile_slug]/
├── +page.server.ts         # Server-side data fetching
├── +page.svelte            # Main page component
├── +layout.svelte          # Layout with navigation
├── components/
│   ├── SourcefileHeader.svelte
│   ├── SourcefileText.svelte  
│   ├── SourcefileWords.svelte
│   └── SourcefilePhrases.svelte
└── words/+page.svelte      # Words tab view
```

4. **TypeScript Interface**:

```typescript
interface SourcefileAPIResponse {
  success: boolean;
  sourcefile: {
    id: number;
    filename: string;
    slug: string;
    description: string | null;
    sourcefile_type: 'text' | 'image' | 'audio' | 'youtube_audio';
    text_target: string | null;
    text_english: string | null;
    has_audio: boolean;
    has_image: boolean;
  };
  sourcedir: {
    id: number;
    path: string;
    slug: string;
    language_code: string;
  };
  enhanced_text: string | null;
  wordforms: Array<Wordform>;
  phrases: Array<Phrase>;
  metadata: {
    created_at: string;
    updated_at: string;
    image_processing?: {
      original_size: number;
      final_size: number;
      was_resized: boolean;
    };
  };
  navigation: {
    current_position: number;
    total_files: number;
    is_first: boolean;
    is_last: boolean;
    prev_slug?: string;
    next_slug?: string;
  };
  stats: {
    wordforms_count: number;
    phrases_count: number;
    already_processed: boolean;
  };
}
```

### Progress Update (March 30, 2023)

#### API Implementation

We've made significant progress on the API side:

1. **New Pattern for API Endpoints**:
   - Created a reusable utility function `get_sourcefile_details()` in `utils/sourcefile_utils.py` to:
     - Centralize logic for retrieving sourcefile data
     - Avoid code duplication between view and API functions
     - Make data format consistent between endpoints

2. **Implemented API Endpoints**:
   - Created `inspect_sourcefile_api()` for basic sourcefile metadata
   - Created `inspect_sourcefile_text_api()` for text content and enhanced text
   - Created `inspect_sourcefile_words_api()` for wordforms data
   - Created `inspect_sourcefile_phrases_api()` for phrases data
   - Created `process_sourcefile_api()` for triggering file processing

3. **Code Refactoring**:
   - Moved common logic from view functions to utility functions
   - Standardized response format with consistent fields

#### Current Challenges

1. **API Connection Issues**:
   - Testing with curl shows connection issues to the Flask API
   - Need to verify if Flask server is running on expected port (3000)
   - May need to check CORS settings if SvelteKit frontend encounters issues

2. **Data Structure Complexity**:
   - Working with nested data structures (sourcefile contains wordforms, phrases)
   - Need to ensure proper typing on the SvelteKit side

3. **Linter Errors**:
   - Import error for `get_sourcefile_details` in `sourcefile_api.py` which needs to be fixed
   - TypeScript errors in SvelteKit frontend related to API response types

#### Next Steps

1. **Debug API Connections**:
   - Verify Flask server is running and accessible
   - Test API endpoints directly with curl
   - Fix any import or linter errors

2. **Continue SvelteKit Implementation**:
   - Update the frontend page structure based on available API data
   - Break down the sourcefile page into reusable components
   - Implement navigation between tabs and files

3. **Enhance Error Handling**:
   - Improve error handling in both API and frontend
   - Add proper loading states in SvelteKit
   - Provide fallbacks for missing data

4. **Documentation**:
   - Document API endpoints and expected response formats
   - Create TypeScript interfaces for API responses

By taking a modular approach with shared utilities, we're making the codebase more maintainable while providing consistent data to both Jinja templates and the SvelteKit frontend.

#### Implementation Details

1. **Shared Utility Function**:

```python
def get_sourcefile_details(sourcefile_entry: Sourcefile, target_language_code: str):
    # Gets all details needed for both view and API functions in one place
    # Navigation, wordforms, phrases, enhanced text, metadata, etc.
    # Returns a standardized dictionary structure
```

This approach offers several benefits:
- **Consistency**: Same data structure used in both Jinja templates and SvelteKit
- **DRY Principle**: Avoid duplicating complex data retrieval logic
- **Maintainability**: Changes to data structure only need to be made in one place
- **Performance**: Optimized database queries in one place

2. **API Response Structure**:

```json
{
  "success": true,
  "sourcefile": {
    "id": 123,
    "filename": "example.txt",
    "slug": "example",
    "description": "Example description",
    "sourcefile_type": "text",
    "text_target": "Original text",
    "text_english": "Translated text",
    "has_audio": false,
    "has_image": false
  },
  "sourcedir": {
    "id": 456,
    "path": "Example Directory",
    "slug": "example-directory",
    "language_code": "el"
  },
  "enhanced_text": "<p>Enhanced <a href=\"...\">text</a> with links</p>",
  "wordforms": [...],
  "phrases": [...],
  "metadata": {
    "created_at": "2023-03-30T12:00:00",
    "updated_at": "2023-03-30T12:00:00"
  },
  "navigation": {
    "current_position": 1,
    "total_files": 10,
    "is_first": true,
    "is_last": false
  },
  "stats": {
    "wordforms_count": 5,
    "phrases_count": 3,
    "already_processed": true
  }
}
```

### Detailed Next Actions

1. **Fix API Issues**
   - [ ] Fix the import issue with `get_sourcefile_details` in `sourcefile_api.py`
   - [ ] Check that Flask server is running on port 3000
   - [ ] Test API endpoints with curl to confirm they return the expected data
   - [ ] Address any CORS issues that may arise

2. **SvelteKit Frontend Implementation**
   - [ ] Finish creating the component directories and files
   - [ ] Implement the TypeScript interfaces for API responses
   - [ ] Create API utility functions for fetching sourcefile data
   - [ ] Develop the +page.server.ts file for data fetching

3. **Component Development**
   - [ ] Implement the SourcefileHeader component
   - [ ] Implement the SourcefileText component for the Text tab
   - [ ] Create a basic layout with styling placeholder
   - [ ] Ensure tab navigation works correctly

4. **Process Tab-Specific Components**
   - [ ] Create the Words tab view with data display
   - [ ] Create the Phrases tab view with data display
   - [ ] Implement API calls for tab-specific data
   - [ ] Add tab state retention during navigation

5. **Testing and Documentation**
   - [ ] Test page layout on different screen sizes
   - [ ] Document API response formats in the SvelteKit codebase
   - [ ] Write usage examples for the getApiUrl utility function
   - [ ] Test with various sourcefiles to ensure proper display


    