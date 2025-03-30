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

## SvelteKit Implementation

The SvelteKit implementation aims to replicate all legacy functionality while improving the user experience and maintainability.

### Core Components

- **Routes**:
  - `/language/[language_code]/search/` - Search form page
  - `/language/[language_code]/search/[wordform]/` - Search result handling and redirection

- **Backend Integration**:
  - Type-safe API calls to existing Flask endpoints
  - Client-side navigation for improved performance

- **UI Components**:
  - Bootstrap styling with custom theme
  - Card-based results display
  - Clean, responsive search form

### Current Implementation

The current SvelteKit implementation:

1. Provides a search form that queries the Flask API
2. Handles basic wordform searching and redirection
3. Uses Bootstrap styling with custom theme for consistency
4. Leverages SvelteKit's client-side navigation for better user experience

### Missing Features

Compared to the legacy implementation, the SvelteKit port is still missing:

1. Complete English translation search functionality
2. Rich search results display for multiple matches
3. Some edge case handling for special characters and diacritics
4. Advanced auto-generation of wordforms

## Action Plan for Feature Parity

### Stage 1: Core Search API Integration

- [ ] Complete the wordform API endpoints:
  - [ ] `wordforms_list_api()` in `views/wordform_api.py`
  - [ ] `get_wordform_metadata_api()` in `views/wordform_api.py`
  - [ ] Make sure all search-related endpoints are typed correctly

- [ ] Improve URL handling:
  - [ ] Ensure proper encoding/decoding of special characters
  - [ ] Handle different writing systems consistently

### Stage 2: Search Results Page

- [ ] Create reusable components for search results:
  - [ ] `SearchResultsList.svelte` for displaying categorized results
  - [ ] `SearchSuggestions.svelte` for displaying suggestions for invalid words

- [ ] Implement full translation search results:
  - [ ] Category display (exact matches, possible matches, translations)
  - [ ] Handle multiple results with proper sorting and grouping

### Stage 3: Advanced Features

- [ ] Add auto-generation of valid wordforms:
  - [ ] Connect to wordform generation API
  - [ ] Handle redirects for newly generated wordforms

- [ ] Implement lemma priority redirects:
  - [ ] Check if search term is a lemma and redirect accordingly
  - [ ] Preserve special priority rules from legacy implementation

- [ ] Add enhanced error handling:
  - [ ] Informative messages for invalid words
  - [ ] Suggestions for potential misspellings

### Stage 4: User Experience Improvements

- [ ] Add search history:
  - [ ] Save recent searches in localStorage
  - [ ] Provide quick access to previous searches

- [ ] Enhance search form:
  - [ ] Add autocomplete suggestions
  - [ ] Improve keyboard navigation

## Implementation Notes

### API Integration

The SvelteKit implementation uses type-safe API calls to the Flask backend, defined in `src/lib/api.ts`:

```typescript
// Example of API call in SvelteKit
const searchResult = await fetchApi(`/api/lang/${languageCode}/search/${encodedWordform}`);
```

### Component Structure

Search-related components use Bootstrap styling with custom theme:

```html
<!-- Example of search form component -->
<form class="mb-4">
  <div class="input-group">
    <input type="text" class="form-control" bind:value={searchTerm} />
    <button class="btn btn-primary" type="submit">Search</button>
  </div>
</form>
```

### Navigation Pattern

SvelteKit uses client-side navigation for improved performance:

```typescript
// Example of redirection logic
if (result.redirect) {
  goto(result.redirect_url);
} else {
  // Display search results
}
```

## Testing Search Functionality

Thorough testing is essential for ensuring search works correctly:

1. **Basic Functionality**:
   - Direct wordform matches
   - Case-insensitive matches
   - Normalized form (without diacritics)

2. **Edge Cases**:
   - Words with diacritics
   - Words in non-Latin scripts
   - Words with special characters
   - Very long search terms

3. **Translation Search**:
   - English words with multiple translations
   - Partial matches in translations
   - Stemmed matches in translations

4. **User Experience**:
   - Response time
   - Error messages clarity
   - Suggestions helpfulness

## Conclusion

The search functionality is a critical part of the HelloZenno application, providing users with a flexible way to discover and learn language content. As we transition from Flask/Jinja to SvelteKit, maintaining feature parity while improving the user experience is our primary goal.

The plan outlined above provides a clear path toward achieving complete feature parity between the legacy and new implementations, ensuring users continue to enjoy a rich, helpful search experience in the SvelteKit version of HelloZenno.