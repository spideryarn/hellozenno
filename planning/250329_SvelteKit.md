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
- [ ] Create `lemmas_list_api()` in `lemma_api.py` (from `lemmas_list_vw()`)
- [ ] Create `phrases_list_api()` in `phrase_api.py` (from `phrases_list_vw()`)
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


    