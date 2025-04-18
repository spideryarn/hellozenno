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
- [x] Create SvelteKit project (done: renamed to `frontend`)
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
- [x] Write up `frontend/README.md` in detail

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
- [x] Create `search_landing_api()` in `search_api.py` (from `search_landing_vw()`)
- [x] Create `search_word_api()` in `search_api.py` (from `search_word_vw()`)

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
- [x] Implemented search functionality with search form and results pages
- [x] Created search API endpoints in Flask backend
- [x] Integrated direct navigation from search to wordform pages

### In Progress
- [ ] Enhance sentence component with more features
- [ ] Implement remaining language-specific routes
- [ ] Complete wordform API endpoints and related SvelteKit pages
- [ ] Finish sourcefile viewing functionality

## Questions

- Best practice for API route structure between SvelteKit and Flask?
- How to handle environment configuration across both services?
- Deployment strategy details for Vercel?

## Sourcefile Page Implementation

### Stages for Implementation

1. **API Backend**
   - [x] Create `inspect_sourcefile_api()` in `views/sourcefile_api.py`
   - [x] Create `inspect_sourcefile_text_api()` in `views/sourcefile_api.py`
   - [x] Create `inspect_sourcefile_words_api()` in `views/sourcefile_api.py`
   - [x] Create `inspect_sourcefile_phrases_api()` in `views/sourcefile_api.py`
   - [x] Test API endpoints with curl or similar tool

2. **SvelteKit Basic Structure**
   - [x] Create route structure for `/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]`
   - [x] Implement server-side data fetching in `+page.server.ts`
   - [x] Create basic layout for the page in `+page.svelte`

3. **Component Breakdown**
   - [x] Create `SourcefileHeader` component
     - [x] Implement file metadata display
     - [x] Add navigation buttons
     - [x] Include sourcefile tabs
   - [x] Create `SourcefileText` component
     - [x] Display the text content
     - [x] Add collapsible translation section

4. **Functionality**
   - [ ] Connect API endpoints to UI actions (process, rename, delete)
   - [ ] Implement tab navigation
   - [ ] Set up previous/next navigation
   - [ ] Add description editing functionality

5. **Later Enhancements**
   - [ ] Implement enhanced text with interactive word links
   - [ ] Add styling to match the original design
   - [ ] Create words and phrases tabs with full functionality

### Progress Update (March 30, 2025)

#### Current Status of Sourcefile Pages

1. **API Implementation (Completed)**:
   - All necessary API endpoints have been implemented in `sourcefile_api.py`:
     - `inspect_sourcefile_api()` for basic metadata
     - `inspect_sourcefile_text_api()` for text content
     - `inspect_sourcefile_words_api()` for wordforms data
     - `inspect_sourcefile_phrases_api()` for phrases data
     - `process_sourcefile_api()` for processing files
     - Other utility APIs for updating, renaming, deleting files

2. **SvelteKit Frontend (Partially Complete)**:
   - Basic route structure created
   - Server-side data fetching implemented in `+page.server.ts`
   - Main page component created with tab navigation
   - `SourcefileHeader` and `SourcefileText` components implemented
   - Layout and styling matches the design
   - We've added `SourcefileWords` and `SourcefilePhrases` components
   - Connected API endpoints to UI actions (process, rename, delete, update description)

3. **Current Issues**:
   - The problem with `/language/el/source/250309-jason-ch-11/1000010996-jpg` URL:
     - API endpoints are correctly set up and returning data (as we verified with curl)
     - The issue may be in the SvelteKit routing or how parameters are passed
     - We should check if the `+page.svelte` is accessing the props correctly

#### Next Steps

1. **Fix Rendering Issues**:
   - [ ] Debug the specific issue with `1000010996-jpg` URL
   - [x] Ensure consistent prop passing between parent and child components
   - [x] Fix the error related to missing `language_name`

2. **Connect Frontend Actions to API**:
   - [x] Implement process button functionality
   - [x] Add rename and delete actions
   - [x] Connect description editing to API

3. **Complete Tab Functionality**:
   - [x] Create `SourcefileWords` and `SourcefilePhrases` components
   - [x] Implement tab state maintenance between navigation
   - [x] Connect tab content to the appropriate API endpoints

4. **Implement Missing Components**:
   - [x] Create the Words tab to display wordforms
   - [x] Create the Phrases tab to display phrases
   - [ ] Add appropriate loading states

5. **Testing and Refinement**:
   - [ ] Test navigation between files
   - [ ] Test all API actions (process, rename, delete)
   - [ ] Optimize data loading to reduce redundant fetches

### Specific Action Items

1. **Fix the `language_name` Error**:
   - [x] Check if it's properly passed from `+page.server.ts` to `+page.svelte`
   - [x] Consider using `get_language_name` API consistently

2. **Connect API Actions**:
   - [x] Update the `saveDescription()` method in `SourcefileHeader.svelte` to call the API
   - [x] Implement functionality for the Process button
   - [x] Add confirmation dialog for delete action

3. **Check Route Parameters**:
   - [ ] Verify the structure of all API endpoint URLs
   - [ ] Ensure `sourcedir_slug` and `sourcefile_slug` parameters are correctly passed

4. **Additional Final Steps**:
   - [ ] Add loading indicators for API actions
   - [ ] Improve error handling and user feedback
   - [ ] Test across different file types (text, image, audio)
   - [ ] Document the API response structures for future reference

By addressing these items, we should be able to get the Sourcefile pages fully functional.

## Progress Summary (March 30, 2025)

Today we've made significant progress on the Sourcefile page implementation:

1. **Fixed the URL API Structure**:
   - Updated the `sourcefiles_for_sourcedir_api` route in `sourcedir_api.py` to use the path `/<target_language_code>/<sourcedir_slug>` instead of `/<target_language_code>/<sourcedir_slug>/files` for better URL structure consistency.

2. **Created Missing Components**:
   - Implemented `SourcefileWords.svelte` to display wordforms from a sourcefile
   - Implemented `SourcefilePhrases.svelte` to display phrases from a sourcefile
   - Updated the main page component to use these new components

3. **Connected API Actions**:
   - Implemented process button functionality for analyzing text
   - Added sourcefile renaming capability
   - Added sourcefile deletion with confirmation
   - Implemented description editing
   - Fixed the `language_name` error by properly passing it from `+page.server.ts`

4. **Enhanced UI**:
   - Improved tab functionality to display appropriate content
   - Added error handling for API actions
   - Improved the component structure for better maintainability

### Recommendations for Testing

The remaining issue with accessing the URL `/language/el/source/250309-jason-ch-11/1000010996-jpg` should be addressed by:

1. **Testing the API Directly**:
   ```bash
   curl -v http://localhost:3000/api/lang/sourcefile/el/250309-jason-ch-11/1000010996-jpg
   curl -v http://localhost:3000/api/lang/sourcefile/el/250309-jason-ch-11/1000010996-jpg/text
   ```

2. **Checking the SvelteKit Browser Console**:
   - Open the browser's developer tools when visiting the problem URL
   - Look for any errors in the console related to data fetching or rendering

3. **Verifying Props in Component Chain**:
   - Add temporary logging in the `+page.server.ts` to confirm data is being fetched correctly
   - Check if `textData.sourcefile` and related objects exist

4. **Testing Other Routes**:
   - Check if other sourcefile URLs work correctly
   - Test whether the tabs function correctly on working URLs

Once these tests are complete, we should be able to identify the specific issue with the `1000010996-jpg` URL and fix it.

### Next Development Areas

After completing the Sourcefile pages, we should focus on:

1. **Flashcard System**:
   - Implement the flashcard pages for practicing vocabulary
   - Connect the links from the Sourcefile pages to the flashcard system

2. **Authentication**:
   - Implement Supabase authentication in SvelteKit
   - Add protected routes and user profiles

3. **Full Testing**:
   - Create a comprehensive testing plan to ensure all features work together
   - Focus on edge cases and error handling

Our progress on the SvelteKit migration is solid, with most of the core functionality now implemented. The remaining work is primarily refinement, testing, and addressing edge cases.

## Search Functionality Implementation

Search functionality allows users to find words in the target language and view their details. Here's a detailed plan for implementing this feature in SvelteKit:

### API Backend Development
- Create `search_api.py` with Flask API endpoints
  - Implement `search_landing_api()` function to provide data for the search form page
  - Implement `search_word_api()` function to handle word search functionality
  - Ensure proper URL decoding for search queries
  - Add appropriate error handling and validation
  - Update Blueprint registry to include the new API endpoints

### SvelteKit Frontend Development

Frontend Routes Setup
- Create SvelteKit route structure
  - Create `/src/routes/language/[language_code]/search/+page.svelte` for the search landing page
  - Create `/src/routes/language/[language_code]/search/[wordform]/+page.svelte` for search results 
  - Create corresponding server-side data loading files (`+page.server.ts`)

Components and UX
- Implement search form component
  - Create clean, responsive form layout based on Bootstrap styling
  - Handle form submission and validation
  - Include search tips as in the original Jinja template
- Implement appropriate loading states during search
- Add error handling for common search issues
- Ensure proper URL encoding/decoding for search terms

Integration and Testing
- Connect with Flask backend API using typed routes
  - Use `getTypedApiUrl` utility for type-safe API URLs
  - Handle API responses and errors appropriately
- Test search functionality
  - Test empty, valid, and invalid search terms
  - Test special characters and non-Latin scripts
  - Verify redirect behavior to wordform view
  - Check URL encoding/decoding works correctly

### Action Stages

Backend API Implementation
- [x] Create `views/search_api.py` file with Blueprint setup
- [x] Refactor common search functionality to a utility module if needed
- [x] Implement `search_landing_api()` endpoint for search form data
- [x] Implement `search_word_api()` endpoint to handle search queries
- [x] Add appropriate error handling and validation
- [x] Test API endpoints with curl or similar tool

SvelteKit Search Landing Page Implementation
- [x] Create route files for search landing page
- [x] Implement form component with Bootstrap styling
- [x] Add language name fetching from API
- [x] Include search tips section
- [x] Connect form submission to search functionality
- [x] Add appropriate loading state indicators

SvelteKit Search Results Implementation
- [x] Create route files for search results page
- [x] Implement redirect to wordform view
- [x] Handle search term parameter extraction
- [x] Add error handling for failed searches
- [x] Implement loading states during redirection


### Detailed Component Structure

Search Landing Page
- `+page.svelte`: Main page component with search form
  - Title and header showing the target language name
  - Search form with input field and submit button
  - Search tips card with information about search functionality
- `+page.server.ts`: Server-side data fetching
  - Get the language name for the given language code
  - Prepare data for the template

Search Word Page
- `+page.svelte`: Minimal component that redirects to wordform view
  - Loading indicator while redirection is in progress
- `+page.server.ts`:
  - Call the backend API to process the search term
  - Handle redirection to the appropriate wordform view

The search functionality will be built with a clean, simple UI following the existing Bootstrap-based styling system as outlined in the STYLING.md document.

## Search Functionality Progress

We have successfully implemented the search functionality in SvelteKit:

### Backend API Implementation
- Created `search_api.py` with Flask API endpoints:
  - Implemented `search_landing_api()` for providing search form data 
  - Implemented `search_word_api()` for processing search requests and providing redirection information
  - Added proper URL decoding for search queries
  - Registered the new API blueprint in the Flask application

### Frontend Implementation
- Created SvelteKit routes for search functionality:
  - Implemented `/language/[language_code]/search/+page.svelte` for the search form
  - Added proper server-side data loading in `+page.server.ts`
  - Implemented direct navigation to wordform pages upon search

### UX Considerations
- Followed Bootstrap styling guidelines for responsive design
- Maintained consistent UI with the rest of the application 
- Provided helpful search tips for users
- Implemented clean form handling and validation

### Issues Encountered and Resolved
- Initially attempted to use the search API for redirection, but faced issues with handling API-based redirects in SvelteKit
- Simplified the approach by directly navigating to the wordform page from the client-side
- Fixed API URL construction to ensure proper communication with the Flask backend

The search functionality now provides a clean, user-friendly interface for searching words in any language. Users can enter a word and be taken directly to the corresponding wordform details page. The implementation follows the established patterns in the codebase and maintains consistency with the rest of the application.

## Type-Safe Route Integration

We've implemented a powerful type-safe route integration system between Flask and SvelteKit:

### Completed:

- [x] Updated Flask's URL registry system to generate TypeScript definitions at `frontend/src/lib/generated/routes.ts`
- [x] Created type-safe utility functions in SvelteKit:
  - [x] `getApiUrl<T extends RouteName>` for generating typed API URLs
  - [x] `apiFetch<T extends RouteName, R>` for type-safe API requests
- [x] Standardized parameter naming using `target_language_code` for API calls

This approach takes advantage of the fact that we're planning to eventually deprecate Flask/Jinja routes, making this a good time to update the Flask URL structure to match our SvelteKit conventions rather than the other way around.

## Search Functionality - Implementation Complete (April 2, 2025)

We have successfully implemented the search functionality in SvelteKit:

### Completed:

- [x] Created backend API endpoints in `views/search_api.py`:
  - [x] Implemented `search_landing_api()` in `search_api.py` that provides data for the search form
  - [x] Implemented `search_word_api()` in `search_api.py` that handles word search and returns redirect information
  - [x] Added proper URL handling with decoding for search queries
  - [x] Registered the new API blueprint in the Flask application

- [x] Implemented SvelteKit frontend:
  - [x] Created `/language/[language_code]/search/+page.svelte` for the search form
  - [x] Created `/language/[language_code]/search/[wordform]/+page.svelte` for handling direct navigation
  - [x] Added proper server-side data fetching in corresponding `+page.server.ts` files
  - [x] Implemented form submission and validation
  - [x] Added responsive styling with Bootstrap

- [x] Improved user experience:
  - [x] Added search tips section to guide users
  - [x] Implemented direct navigation to wordform pages upon search
  - [x] Added loading states for better feedback
  - [x] Added error handling for failed searches
  - [x] Ensured responsive design works across device sizes

### Issues Solved:

- Initially attempted to use the search API for redirection, but faced challenges with API-based redirects in SvelteKit
- Simplified the approach to navigate directly to the wordform page from the client-side
- Fixed API URL construction to ensure proper communication with the Flask backend
- Ensured proper handling of special characters and non-Latin scripts in search terms

### Next Steps:

Based on our successful implementation of search functionality, we recommend focusing on the following API endpoints next:

1. **Wordform API Endpoints**:
   - Create `wordforms_list_api()` in `wordform_api.py` (from `wordforms_list_vw()`)
   - Create `get_wordform_metadata_api()` in `wordform_api.py` (from `get_wordform_metadata_vw()`)
   - Create `delete_wordform_api()` in `wordform_api.py` (from `delete_wordform_vw()`)

2. **Sourcefile API Endpoints**:
   - Continue work on remaining sourcefile-related endpoints to complete the sourcefile viewing functionality

3. **Flashcard API**:
   - Create `flashcard_landing_api()` in `flashcard_api.py` (from `flashcard_landing_vw()`)

By focusing on these areas next, we can build upon our existing search functionality and create a more complete language learning experience in SvelteKit.


    