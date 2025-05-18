# Search Functionality

This document provides a comprehensive overview of the search functionality in HelloZenno, comparing the legacy Flask/Jinja implementation with the new SvelteKit port. It outlines current functionality, implementation details, and remaining work to achieve feature parity.

## Search Behavior Overview

HelloZenno's search functionality is designed to be flexible and user-friendly, supporting:

- Target language wordform search (direct matches, case-insensitive matches, and normalized matches)
- English translation search (finding target language words via their English translations)
- Automatic redirection to lemma pages when appropriate
- Handling of invalid or unrecognized words
- Various edge cases like diacritics, special characters, and misspellings

## Legacy Implementation (Flask/Jinja)

The legacy search implementation is feature-rich and handles a wide range of search scenarios.

### Core Components

- **API Endpoints**: `views/search_api.py`
- **View Controllers**: `views/search_views.py`
- **Templates**: `templates/search.jinja`, `templates/translation_search_results.jinja`
- **Utilities**: `utils/search_utils.py`, `utils/word_utils.py`
- **Wordform Handling**: `views/wordform_views.py`

### Search Flow

```
User Input
    |
    v
[Search Form] --> [search_views.py] --> [GET /language/{lang}/search/{wordform}]
    |                                       |
    |                                       v
    |                     +----------------[Wordform Exists?]----------------+
    |                     |                                                  |
    |                     v                                                  v
    |               [Yes, Exact Match]                        [No Exact Match]
    |                     |                                           |
    |                     v                                           v
    |               [Redirect to Wordform]          [Try Case-Insensitive Match]
    |                                                         |
    |                                                         v
    |                                       +------[Found Case-Insensitive?]------+
    |                                       |                                     |
    |                                       v                                     v
    |                                   [Yes]                                   [No]
    |                                     |                                       |
    |                                     v                                       v
    |                     [Redirect to Case-Insensitive Match]   [Try Normalized Form]
    |                                                                     |
    |                                                                     v
    |                                                  +-------[Found Normalized?]-------+
    |                                                  |                                 |
    |                                                  v                                 v
    |                                              [Yes]                               [No]
    |                                                |                                   |
    |                                                v                                   v
    |                                 [Redirect to Normalized Match]     [Check if English Word]
    |                                                                             |
    |                                                                             v
    |                                                              +----[English Matches?]----+
    |                                                              |                         |
    |                                                              v                         v
    |                                                    [Multiple Matches]           [No Matches]
    |                                                             |                         |
    |                                                             v                         v
    +--------------------------------------------[Show Search Results]           [Show Invalid Word]
```

### Key Functions

1. **Entry Points**:
   - `search_landing_vw()`: Renders the search form page
   - `search_word_vw()`: Processes search queries and redirects accordingly

2. **Wordform Processing**:
   - `get_wordform_metadata_vw()`: Core function that:
     - Tries exact, case-insensitive, and normalized matches
     - Handles redirection logic
     - Processes multiple matches and invalid words

3. **Search Utilities**:
   - `prepare_search_landing_data()`: Prepares data for search landing page
   - `get_wordform_redirect_url()`: Generates redirect URLs, handling special characters

### Special Behaviors

1. **Lemma Priority**:
   - If a search term matches a lemma directly, it redirects to the lemma page instead of the wordform page
   - The system prioritizes showing the most comprehensive information first

2. **Auto-Generation**:
   - For valid wordforms not in the database, the system generates them on-the-fly
   - Users never see "not found" for valid language wordforms

3. **English Translation Search**:
   - If no direct wordform match is found, the system searches English translations
   - Results are categorized by confidence level and relation to the query

4. **Invalid Word Handling**:
   - Clearly indicates invalid words with helpful suggestions
   - Provides informative feedback on why the search failed

## Current SvelteKit Implementation Status

We've made significant progress on the SvelteKit implementation, focusing on creating a robust and maintainable search experience.

### Completed Work

#### Backend Refactoring

The backend implementation has been refactored for better code sharing and maintainability:

1. **Extracted Common Logic**: 
   - Created a new shared utility function `find_or_create_wordform()` in `utils/word_utils.py`
   - This function encapsulates the complex search logic that was duplicated in both API and view functions
   - Returns a standardized response format with status and data fields

2. **Updated API Endpoints**:
   - Refactored `get_wordform_metadata_api()` in `views/wordform_api.py` to use the shared utility
   - Response format now consistently includes `status` field indicating the type of result

3. **Updated View Functions**:
   - Refactored `get_wordform_metadata_vw()` in `views/wordform_views.py` to use the shared utility
   - Maintains backward compatibility with templates and URL handlers

#### SvelteKit Frontend

The SvelteKit search implementation now includes:

1. **Type Definitions**:
   - Added comprehensive type definitions in `frontend/src/lib/types.ts`
   - Created interfaces for `SearchMatch`, `SearchResultCategory`, and `SearchResults`
   - Ensures type safety throughout the application

2. **API Integration**:
   - Enhanced `api.ts` with a new `getWordformWithSearch()` function that handles complex search results
   - Function properly handles 404 responses for "not found" words
   - Uses type-safe URL generation via `getApiUrl`

3. **Components**:
   - Created a new `SearchResults.svelte` component that displays different result types:
     - Direct matches
     - Multiple matches categorized by source
     - Suggestions for invalid words
     - English translation matches
   - Added a reusable `SearchBarMini.svelte` component for consistent search experience:
     - Used in both language layout and sourcefile pages
     - Provides a compact search interface throughout the application
     - Creates a consistent search experience across all pages

4. **Server-Side Handling**:
   - Updated `+page.server.ts` to process search results and make proper routing decisions:
     - Redirects for exact matches
     - Renders search results for multiple matches
     - Shows invalid word templates with suggestions

5. **Client-Side Integration**:
   - Enhanced `+page.svelte` to render the search results component
   - Added proper page title and layout integration
   - Handles missing language name by fetching from parent layout data

### Testing Strategy

To test the search functionality thoroughly, follow this testing plan:

1. **Basic Search**:
   - Search for existing wordforms (e.g., "apple" in English)
   - Verify direct navigation to wordform page
   - Check display of metadata and related information

2. **Case Sensitivity**:
   - Search for words with different casing (e.g., "Apple" vs "apple")
   - Verify both lead to the same result
   - Check normalization for languages with diacritics

3. **Multiple Results**:
   - Search for ambiguous terms that match multiple words
   - Verify the search results page displays properly categorized results
   - Test clicking on results navigates to correct pages

4. **English Translation Search**:
   - Search for English words like "house" in a non-English language
   - Verify target language results are displayed
   - Check categorization of results by confidence level

5. **Invalid Words**:
   - Enter non-existent words or deliberate misspellings
   - Verify helpful error messages and suggestions appear
   - Test if suggestions link to valid wordforms

6. **Special Characters**:
   - Test words with diacritics (e.g., Greek "αγάπη")
   - Test words with special characters
   - Verify URL encoding/decoding works correctly

7. **Edge Cases**:
   - Very long words
   - Words with mixed scripts
   - Words containing numbers or symbols
   - Empty search terms

To perform these tests, you would:
1. Start both the Flask server and SvelteKit server
2. Navigate to the search page for a specific language (e.g., `/language/el/search`)
3. Enter different search terms and verify the behavior
4. Use browser developer tools to monitor network requests and responses
5. Verify the UI properly displays all search result categories

## Appendix: Wordform Page Loading Flow (`/language/{lang}/wordform/{word}`)

This appendix details the sequence of events when a user accesses a specific wordform page.

```mermaid
sequenceDiagram
    participant User
    participant Browser (SvelteKit Frontend)
    participant SvelteKit Server
    participant Flask Backend API
    participant Database
    participant Auth Service (Supabase)

    User->>+Browser (SvelteKit Frontend): Navigate to /language/{lang}/wordform/{word}
    Browser (SvelteKit Frontend)->>+SvelteKit Server: Request page data (SSR Load)
    SvelteKit Server->>SvelteKit Server: Extract lang, wordform from params
    SvelteKit Server->>+Flask Backend API: GET /api/lang/word/{lang}/{word} (via apiFetch, includes token if logged in)

    Flask Backend API->>Flask Backend API: Decorator @api_auth_optional
    Flask Backend API->>Auth Service (Supabase): (If token present) Verify JWT
    Auth Service (Supabase)-->>Flask Backend API: Validation result (sets g.user/g.profile or None)

    Flask Backend API->>Flask Backend API: Call find_or_create_wordform(lang, word)
    Flask Backend API->>+Database: Query Wordform (exact, case-insensitive, normalized)
    alt Wordform Found
        Database-->>-Flask Backend API: Return Wordform data
        Flask Backend API->>Flask Backend API: status = "found"
    else Wordform NOT Found
        Flask Backend API->>Flask Backend API: Check if generation needed/allowed
        alt Generation Allowed (User Logged In OR Free)
            Flask Backend API->>Flask Backend API: Generate metadata (LLM, dict, etc.)
            Flask Backend API->>+Database: INSERT new Wordform
            Database-->>-Flask Backend API: New Wordform data
            Flask Backend API->>Flask Backend API: status = "generated"
        else Generation Requires Auth (User NOT Logged In)
            Flask Backend API->>Flask Backend API: Raise AuthenticationRequiredForGenerationError
            Note right of Flask Backend API: Caught by API endpoint wrapper
            Flask Backend API->>Flask Backend API: status = "requires_authentication"
            Flask Backend API-->>-SvelteKit Server: 401 Response {"authentication_required_for_generation": true}
            SvelteKit Server-->>-Browser (SvelteKit Frontend): Return auth required data
            Browser (SvelteKit Frontend)-->>-User: Display "Login Required" message
            User-->>User: End Flow (Requires Auth)
        else Invalid Word
            Flask Backend API->>Flask Backend API: status = "invalid_word"
            Flask Backend API->>Flask Backend API: (Optional) Find suggestions
        end
    end

    opt Wordform Found or Generated AND has lemma_id
        Flask Backend API->>+Database: Query Lemma data by lemma_id
        Database-->>-Flask Backend API: Return Lemma data
        Flask Backend API->>Flask Backend API: Add lemma_metadata to response
    end

    Flask Backend API-->>-SvelteKit Server: 200 OK Response (JSON: wordform_metadata, lemma_metadata, status, ...)
    SvelteKit Server-->>-Browser (SvelteKit Frontend): Return fetched page data (wordformData)
    Browser (SvelteKit Frontend)->>Browser (SvelteKit Frontend): Render +page.svelte with wordformData
    alt isValidData is true
        Browser (SvelteKit Frontend)-->>User: Display Wordform & Lemma Details
    else
        Browser (SvelteKit Frontend)-->>User: Display Loading/Error/Invalid Word message
    end
    User-->>User: End Flow (Success/Error)

```

**Steps:**

1.  **Navigation & SSR Load:** User goes to the URL. SvelteKit's server `load` function runs.
2.  **API Call:** The `load` function calls the backend API endpoint (e.g., `/api/lang/word/el/μήλο`) using `apiFetch`, including the auth token if the user is logged in (handled via `locals.supabase`).
3.  **Backend Authentication:** The API endpoint uses `@api_auth_optional`. If a token is present, it's verified, setting `g.user`. If not, `g.user` is `None`.
4.  **Core Logic (`find_or_create_wordform`):**
    *   **Lookup:** Tries to find the wordform in the database (exact, case-insensitive, normalized).
    *   **Found:** If successful, retrieves existing data.
    *   **Not Found:**
        *   Checks if generation is needed and if the user is authenticated (`g.user` exists).
        *   **Generate:** If allowed (user logged in or feature is free), generates metadata, creates a DB record, and returns the new data.
        *   **Requires Auth:** If generation needs auth but `g.user` is `None`, raises `AuthenticationRequiredForGenerationError`. The API endpoint catches this and returns a `401` response with `{ "authentication_required_for_generation": true }`.
        *   **Invalid:** If the word is deemed invalid, returns an "invalid\_word" status, possibly with suggestions.
5.  **Lemma Data Fetch:** If the wordform was found/generated and has a `lemma_id`, fetch the associated `Lemma` data.
6.  **API Response:** The backend sends a JSON response containing `wordform_metadata`, `lemma_metadata` (if applicable), `status`, language info, etc., or the `401` error.
7.  **Frontend Rendering:**
    *   The SvelteKit page receives the data.
    *   If `authentication_required_for_generation` is true, it shows a login prompt.
    *   Otherwise, it checks if `wordform_metadata` is present (`isValidData`).
    *   If `isValidData`, it renders the wordform details, translations, lemma information (via `LemmaDetails` component), etc.
    *   If not `isValidData`, it shows a loading or error state.
