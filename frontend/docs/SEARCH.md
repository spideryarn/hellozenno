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

### Recent Progress

We've recently enhanced the search functionality with several important improvements:

1. **Integration Between Wordform and Search**:
   - ✅ Updated wordform page to handle enhanced search responses
   - ✅ Fixed direct wordform access for English translation searches 
   - ✅ Added proper redirection logic between search and wordform pages
   - ✅ Implemented robust error handling for invalid words

2. **Learned Lessons**:
   - The enhanced search API needs to be used consistently across the application
   - Special care must be taken with URL encoding for non-Latin scripts
   - Status-based response handling provides a consistent way to manage different search results
   - Error handling should redirect to appropriate pages rather than showing generic errors

### Remaining Work

The following items still need to be completed:

1. **Lemma Priority**:
   - [ ] Update search logic to check if search term is a lemma
   - [ ] Redirect to lemma page instead of wordform page when appropriate
   - [ ] Update TypeScript types for lemma redirect responses

2. **Error Handling Improvements**:
   - [x] Add more detailed error messages for specific error cases
   - [x] Redirect to search page instead of showing generic errors
   - [ ] Improve handling of timeout scenarios
   - [ ] Add retry logic for intermittent connection issues

3. **UI Enhancements**:
   - [x] Add loading indicators for search in progress
   - [ ] Further improve styling of search result categories
   - [ ] Add visual grouping for related results
   - [ ] Make sure all texts are i18n ready

4. **Performance Optimizations**:
   - [ ] Add caching for common search terms
   - [ ] Optimize API response size
   - [ ] Add debouncing for rapid searches
   - [ ] Consider implementing local search index for basic matches

5. **Accessibility**:
   - [ ] Ensure proper keyboard navigation for search results
   - [ ] Add proper ARIA labels and roles
   - [ ] Test with screen readers

6. **Testing**:
   - [ ] Add comprehensive tests for various search scenarios
   - [ ] Test with multiple languages and character sets
   - [ ] Test English translation search thoroughly

### Implementation Notes

The current implementation follows these key architectural patterns:

1. **Status-based Response Handling**:
   - Backend returns responses with a `status` field indicating the type of result:
     - `"found"`: Direct match found
     - `"multiple_matches"`: Multiple possible matches
     - `"redirect"`: Should redirect to another word
     - `"invalid"`: Invalid word or no matches

2. **Type-Safe API Integration**:
   - Uses the `getApiUrl()` function with route enum values
   - Example: 
     ```typescript
     const url = getApiUrl(RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API, { 
       target_language_code, wordform 
     });
     ```

3. **Component Composition**:
   - Main search page delegates to `SearchResults.svelte` for result display
   - Separation of server-side logic in `+page.server.ts` and client rendering in `+page.svelte`

4. **Error Handling Strategy**:
   - 404 errors for invalid words are processed specially, returning structured data
   - Network errors are properly propagated to display user-friendly messages

## How to Continue Development

To continue developing the search functionality:

1. Focus on implementing the remaining items from the "Remaining Work" section
2. Start with the lemma priority feature, as it provides the most direct user benefit
3. Test each change thoroughly against both common and edge cases
4. Ensure backward compatibility with existing URLs and behaviors

If you encounter edge cases or API inconsistencies during development:
1. First, check the behavior in the legacy Flask/Jinja implementation
2. Consider updating the common utility function in `utils/word_utils.py`
3. Update both the API and view functions to maintain consistency
4. Update the SvelteKit implementation to handle the new behavior

Remember to test with real language data, especially:
- Languages with non-Latin scripts (Greek, Arabic, etc.)
- Words with diacritics and special characters
- Languages with distinct case rules

## Conclusion

The search functionality is a critical part of the HelloZenno application, providing users with a flexible way to discover and learn language content. The current implementation has made significant progress toward feature parity with the legacy system while leveraging modern SvelteKit patterns.

By following the specified remaining work items and testing strategy, the SvelteKit implementation can achieve complete feature parity while improving the user experience through faster client-side navigation and more responsive interactions.