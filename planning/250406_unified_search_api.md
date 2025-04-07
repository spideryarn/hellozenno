# Unified Search API Implementation Plan

This document outlines a detailed plan for implementing a unified search API for the Hello Zenno SvelteKit frontend. The goal is to replace the current multi-endpoint approach with a single unified endpoint that returns consistent data structures, allowing the frontend to handle routing and presentation decisions.

## Background

For background info:
  - frontend/README.md
  - planning/250406_unified_search_api.md
  - frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md
  - frontend/docs/BACKEND_FLASK_API_INTEGRATION.md
  - frontend/docs/SEARCH.md (may be out of date)
  - backend/views/search_api.py
  - frontend/src/routes/language/[language_code]/search/+page.server.ts
  - backend/prompt_templates/quick_search_for_wordform.jinja


The current implementation uses multiple endpoints with server-side redirects:
1. User searches for a word
2. Server decides: redirect to wordform/lemma page, show search results, or show invalid word
3. Different templates are rendered server-side based on these decisions

The new unified approach will:
1. Provide a single API endpoint that returns all search results data in a consistent format
2. Let the client (SvelteKit) handle the routing/rendering decisions
3. Enable a more fluid user experience without full page reloads
4. Maintain all current search behavior and functionality but with a cleaner architecture

**Key Files and Functions**:
- `backend/utils/word_utils.py`: Contains `find_or_create_wordform()` which is the key function for handling search logic
- `backend/prompt_templates/quick_search_for_wordform.jinja`: Used for LLM-powered search when a term doesn't exist in the database
- `backend/views/search_api.py`: Contains the API endpoints for search
- `frontend/src/lib/components/SearchResults.svelte`: The component for displaying search results
- `frontend/src/routes/language/[language_code]/search/+page.svelte`: The search page component

**Development Environment**:
- SvelteKit frontend port = 5173
- Flask backend API port = 3000

## Implementation Stages

## Implementation Progress

### Stage 1: Create Unified Search API Endpoint (COMPLETED)

We have successfully implemented the first stage of the unified search API. This involved creating a new endpoint in the Flask backend and updating the SvelteKit frontend to use it.

#### Backend Changes

Created a new `unified_search_api` endpoint in `backend/views/search_api.py`

Key features of this implementation:
- Leverages the existing `find_or_create_wordform` function for search logic
- Returns a consistent JSON structure for all search outcomes
- Handles empty queries with a specific status
- Provides comprehensive error handling
- All responses include the original query, language code, and language name


#### Frontend Changes

Updated the frontend to use the new unified search API:

1. Added a new `SearchResult` type in `frontend/src/lib/types.ts`:
   ```typescript
   export interface SearchResult {
       status: 'found' | 'multiple_matches' | 'redirect' | 'invalid' | 'empty_query' | 'error';
       query: string;
       target_language_code: string;
       target_language_name: string;
       data: any; // Contains different data based on the status
       error?: string;
   }
   ```

2. Created a new `unifiedSearch` function in `frontend/src/lib/api.ts`

3. Updated the search page component to use the new API and handle all possible response statuses

#### Testing & Validation

The implementation has been tested with various search scenarios:
- Empty query → returns empty_query status
- Exact word match → returns found status with wordform data
- Multiple possible matches → returns multiple_matches status with all options
- Misspellings → returns suggestions in possible_misspellings field
- English words → returns target language translations
- Invalid words → returns invalid status with helpful feedback

All status types properly render the appropriate UI components based on the returned data.

#### Future Improvements

While the basic implementation is complete, there are a few potential improvements to consider:
- Better handling of accented characters and case variations
- Performance optimization for frequently searched terms
- Enhancements to the search results presentation

### Next Stages: Planning

Below are the planned next stages for enhancing the search functionality. These are based on our discussions and analysis of the current implementation.

### Stage 2: Complete API Integration and Refine Frontend Experience

#### 2.1: Type-Safe API Integration

Since we've already implemented a basic version of the search API, the next step is to properly integrate it into the SvelteKit type system. This includes:

1. **Enhance Type Definitions**:
   - Create more specific types for different search result statuses
   - Add proper typing for WordformMetadata and LemmaMetadata
   - Ensure consistent typing across frontend and backend

2. **Add Generated API Routes**:
   - Update the route generation to include the unified search endpoint
   - Use the `RouteName` enum for type-safe API URLs

3. **API Error Handling Improvements**:
   - Add better error messages for network failures
   - Handle rate limiting and timeout scenarios
   - Implement retry logic for transient failures

#### 2.2: Search Component Refinements

Improve the search components:

1. **SearchResults Component**:
   - Refactor to use smaller, more focused components
   - Implement proper Bootstrap styling
   - Better handling of empty states

2. **Performance Optimizations**:
   - Implement debouncing for search input
   - Add loading states and skeleton loaders
   - Consider client-side caching for recent searches

3. **Accessibility Improvements**:
   - Ensure all components are keyboard navigable
   - Add proper ARIA attributes for screen readers
   - Improve focus management and tab order


- **Normalization Behavior**: The complex normalization behavior (handling of accents, case variations, etc.) is handled by the existing backend code, specifically in `word_utils.py`. We've decided to keep this unchanged to avoid introducing new issues.

- **Backward Compatibility**: We don't need to maintain compatibility with the old Flask/Jinja templates since we're migrating completely to SvelteKit.

- **Error Handling**: We've implemented clear error handling that fails loudly and immediately rather than masking issues.

## Implementation Details & Technical Notes

Here are some technical details and implementation notes that are helpful for future reference:

### Core Function: `find_or_create_wordform`

The `find_or_create_wordform` function in `utils/word_utils.py` is the heart of our search functionality:

```python
def find_or_create_wordform(target_language_code: str, wordform: str):
    """
    Find or create a wordform, handling common search behavior.

    This shared utility function handles the common logic used by both
    get_wordform_metadata_vw and get_wordform_metadata_

    Args:
        target_language_code: The language code (e.g. 'el' for Greek)
        wordform: The wordform text

    Returns:
        A dictionary with the following structure:
        {
            "status": str, # "found", "multiple_matches", "redirect", or "invalid"
            "data": dict,  # The result data appropriate for the status
        }
    """
    # [Implementation details omitted for brevity]
```

This function handles:
- Exact matches (returns "found" status)
- Multiple matches (returns "multiple_matches" status)
- Words needing creation (returns "redirect" status)
- Invalid words (returns "invalid" status with possible suggestions)

### LLM-Based Search with Claude

When a word isn't found in the database, the system uses Claude to analyze it via the `quick_search_for_wordform` function, which uses the prompt template in `prompt_templates/quick_search_for_wordform.jinja`. This allows for:

- Identification of inflected forms 
- Matching against lemmas
- English translation searches
- Misspelling detection and suggestions

### Response Structure

The unified API uses a consistent response structure:

```json
{
  "status": "found|multiple_matches|redirect|invalid|empty_query|error",
  "query": "original search query",
  "target_language_code": "el",
  "target_language_name": "Greek",
  "data": {
    // Status-specific data structure
  },
  "error": "Optional error message"
}
```

### Frontend Component Architecture

The frontend uses a flexible component architecture:
- Main search page handles search logic and state management
- Status-specific components render different result types
- Server-side loading provides initial search results for SEO
- Client-side navigation enhances user experience for subsequent searches

## Resources & References

- [Frontend Architecture](../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)
- [API Integration](../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md)
- [SEARCH.md](../frontend/docs/SEARCH.md) (note: somewhat outdated but still useful)
