# Unified Search API Implementation Plan

This document outlines a detailed plan for implementing a unified search API for the Hello Zenno SvelteKit frontend. The goal is to replace the current multi-endpoint approach with a single unified endpoint that returns consistent data structures, allowing the frontend to handle routing and presentation decisions.

## Background

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

Created a new unified search endpoint in `backend/views/search_api.py`:

```python
@search_api_bp.route("/<target_language_code>/unified_search")
def unified_search_api(target_language_code: str):
    """
    Unified search endpoint that handles all search cases in one response.
    Returns a consistent JSON structure regardless of search outcome.
    
    This endpoint replaces the traditional redirect-based search flow with a
    single API that returns all search results data, allowing the client to
    handle presentation decisions.
    
    Status values:
    - empty_query: No search term provided
    - found: Exact wordform match found
    - multiple_matches: Multiple potential matches found
    - redirect: Single match found, but needs redirection (usually to create the wordform)
    - invalid: No matches found
    
    Query params:
    - q: The search query text
    """
    # Get the search query from URL parameters
    query = request.args.get("q", "")
    
    # Handle empty query case
    if not query:
        return jsonify({
            "status": "empty_query",
            "query": "",
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "data": {}
        })
    
    # Normalize query (handle URL encoding)
    query = urllib.parse.unquote(query)
    
    try:
        # Use the existing find_or_create_wordform function
        # This handles all the complex search logic and fallbacks
        result = find_or_create_wordform(target_language_code, query)
        
        # Build a consistent response structure
        response = {
            "status": result["status"],
            "query": query,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "data": result["data"]
        }
        
        return jsonify(response)
    except Exception as e:
        # Log and return a clear error message
        logger.exception(f"Error in unified search: {e}")
        
        # Return error with status code 500
        error_response = {
            "status": "error",
            "query": query,
            "target_language_code": target_language_code,
            "target_language_name": get_language_name(target_language_code),
            "error": str(e),
            "data": {}
        }
        return jsonify(error_response), 500
```

Key features of this implementation:
- Leverages the existing `find_or_create_wordform` function for search logic
- Returns a consistent JSON structure for all search outcomes
- Handles empty queries with a specific status
- Provides comprehensive error handling
- All responses include the original query, language code, and language name

A test script was created in `backend/tests/test_unified_search_api.py` to verify all search scenarios:
- Empty query
- Exact match for existing wordform
- Multiple matches
- Misspellings
- Invalid words
- English translations

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

2. Created a new `unifiedSearch` function in `frontend/src/lib/api.ts`:
   ```typescript
   export async function unifiedSearch(langCode: string, query: string): Promise<SearchResult> {
       if (!query.trim()) {
           return { 
               status: 'empty_query',
               query: '',
               target_language_code: langCode,
               target_language_name: '',
               data: {}
           };
       }
       
       try {
           const response = await fetch(
               `/api/lang/${langCode}/unified_search?q=${encodeURIComponent(query)}`
           );
           
           if (!response.ok) {
               throw new Error(`HTTP error! status: ${response.status}`);
           }
           
           return await response.json();
       } catch (error) {
           console.error('Search error:', error);
           return {
               status: 'error',
               query,
               target_language_code: langCode,
               target_language_name: '',
               error: error instanceof Error ? error.message : 'Unknown error',
               data: {}
           };
       }
   }
   ```

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

#### Discussion Points and Questions

From our conversation, we've addressed several key points:

1. **Using Claude for Search**: We confirmed that we'll continue to use Claude (not GPT-4) via the `quick_search_for_wordform.jinja` template for the LLM-powered search functionality. This works well in production and doesn't need to be changed.

2. **Normalization Behavior**: The complex normalization behavior (handling of accents, case variations, etc.) is handled by the existing backend code, specifically in `word_utils.py`. We've decided to keep this unchanged to avoid introducing new issues.

3. **Backward Compatibility**: We don't need to maintain compatibility with the old Flask/Jinja templates since we're migrating completely to SvelteKit.

4. **Search History**: We've decided to skip implementing search history for now to keep things simple.

5. **Error Handling**: We've implemented clear error handling that fails loudly and immediately rather than masking issues.

### Stage 3: Global Search Integration

For the third stage, we'll focus on making search more accessible throughout the app:

1. **Header Search Component**:
   - Add a search box in the global header
   - Allow searching from any page in the app
   - Context-aware search that defaults to current language

2. **Search URL Improvements**:
   - Add search query parameters to URLs
   - Support deep linking to search results
   - Maintain search state during navigation

3. **Enhanced Results Display**:
   - Improve the organization of search results
   - Add audio previews when available
   - Group results by relevance and type

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

- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Frontend Architecture](../frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md)
- [API Integration](../frontend/docs/BACKEND_FLASK_API_INTEGRATION.md)
- [SEARCH.md](../frontend/docs/SEARCH.md) (note: somewhat outdated but still useful)

## Conclusion

The unified search API represents a significant improvement in the HelloZenno architecture:

1. **Cleaner Separation of Concerns**: Backend handles data, frontend handles presentation
2. **Consistent Data Structures**: All search outcomes use the same base response format
3. **Improved User Experience**: Client-side navigation for faster interactions
4. **Maintainable Codebase**: Clean API design simplifies future enhancements

With Stage 1 complete, we now have a solid foundation for enhancing the search experience in future stages.
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Search error:', error);
        return {
            status: 'error',
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
}
```

#### 2.2: Create Type Definitions

Define TypeScript interfaces for the search results:

```typescript
// src/lib/types/search.ts
export interface BaseSearchResult {
    query: string;
    status: 'found' | 'multiple_matches' | 'redirect' | 'invalid' | 'empty_query' | 'error';
    target_language_code: string;
    target_language_name: string;
}

export interface FoundResult extends BaseSearchResult {
    status: 'found';
    data: {
        wordform_metadata: WordformMetadata;
        lemma_metadata: LemmaMetadata;
        metadata: {
            created_at: string;
            updated_at: string;
        };
    };
}

export interface MultipleMatchesResult extends BaseSearchResult {
    status: 'multiple_matches';
    data: {
        search_term: string;
        target_language_results: {
            matches: WordMatch[];
            possible_misspellings: string[] | null;
        };
        english_results: {
            matches: WordMatch[];
            possible_misspellings: string[] | null;
        };
    };
}

export interface RedirectResult extends BaseSearchResult {
    status: 'redirect';
    data: {
        redirect_to: string;
    };
}

export interface InvalidResult extends BaseSearchResult {
    status: 'invalid';
    data: {
        error: string;
        description: string;
        wordform: string;
        possible_misspellings: string[] | null;
    };
}

export interface EmptyQueryResult extends BaseSearchResult {
    status: 'empty_query';
    data: Record<string, never>;
}

export interface ErrorResult extends BaseSearchResult {
    status: 'error';
    error: string;
}

export type SearchResult = 
    | FoundResult 
    | MultipleMatchesResult 
    | RedirectResult 
    | InvalidResult 
    | EmptyQueryResult
    | ErrorResult;

export interface WordMatch {
    target_language_wordform: string;
    target_language_lemma: string;
    part_of_speech: string;
    english: string[];
    inflection_type: string;
}

// Add interfaces for WordformMetadata and LemmaMetadata based on your data structure
```

#### 2.3: Test the API Service

Create a simple test page to verify the API service works correctly:

```svelte
<!-- src/routes/test-search/+page.svelte -->
<script lang="ts">
    import { searchWord } from '$lib/services/api';
    
    let query = '';
    let result: any = null;
    let loading = false;
    
    async function handleSearch() {
        loading = true;
        result = await searchWord('el', query);
        loading = false;
    }
</script>

<h1>Test Search API</h1>

<form on:submit|preventDefault={handleSearch}>
    <input bind:value={query} placeholder="Enter search term">
    <button type="submit" disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
    </button>
</form>

{#if result}
    <h2>Status: {result.status}</h2>
    <pre>{JSON.stringify(result, null, 2)}</pre>
{/if}
```

### Stage 3: Build Basic Search Page

#### 3.1: Create Search Route

Create the main search page that uses the API service:

```svelte
<!-- src/routes/[lang]/search/+page.svelte -->
<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { searchWord } from '$lib/services/api';
    import type { SearchResult } from '$lib/types/search';
    
    export let data; // From load function
    
    let query = $page.url.searchParams.get('q') || '';
    let result: SearchResult | null = null;
    let loading = false;
    
    async function handleSearch() {
        if (!query.trim()) return;
        
        loading = true;
        
        // Update URL to reflect search
        goto(`/${data.lang}/search?q=${encodeURIComponent(query)}`, { 
            replaceState: true,
            keepFocus: true,
            noScroll: true
        });
        
        result = await searchWord(data.lang, query);
        loading = false;
        
        // Handle immediate redirects for exact matches
        if (result.status === 'redirect') {
            goto(`/${data.lang}/wordform/${result.data.redirect_to}`);
        }
    }
    
    // Perform search on initial load if query exists
    if (query && !result) {
        handleSearch();
    }
</script>

<svelte:head>
    <title>Search {data.langName}</title>
</svelte:head>

<div class="container">
    <h1>Search {data.langName} Words</h1>
    
    <form on:submit|preventDefault={handleSearch}>
        <div class="search-field">
            <input 
                type="text" 
                bind:value={query} 
                placeholder="Enter a word to search..."
                aria-label="Search term"
            >
            <button type="submit" disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>
        </div>
    </form>
    
    {#if loading}
        <div class="loading">Searching...</div>
    {:else if result}
        <div class="results">
            <p>Status: {result.status}</p>
            <!-- We'll replace this with proper components in the next stage -->
            <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
    {/if}
</div>
```

#### 3.2: Create Page Load Function

Create the load function for the search page:

```typescript
// src/routes/[lang]/search/+page.ts
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { getLanguageName } from '$lib/utils/languages';

export const load = (({ params, url }) => {
    const { lang } = params;
    const q = url.searchParams.get('q') || '';
    
    const langName = getLanguageName(lang);
    if (!langName) {
        throw error(404, `Language '${lang}' not found`);
    }
    
    return {
        lang,
        langName,
        query: q
    };
}) satisfies PageLoad;
```

#### 3.3: Test Basic Search Page

Test the search page by navigating to it and performing searches for different scenarios:
- Empty query
- Existing wordform
- Multiple matches
- Misspelling
- Invalid word
- English word

Verify that:
- The URL updates correctly with the search query
- The search results are displayed correctly
- Redirects work correctly for exact matches

### Stage 4: Create Result Components

#### 4.1: Create EmptyState Component

```svelte
<!-- src/lib/components/search/EmptyState.svelte -->
<script lang="ts">
    export let langName: string;
</script>

<div class="empty-state">
    <h2>Search {langName} Words</h2>
    <p>Enter a word to search. You can search for:</p>
    <ul>
        <li>Words in {langName}</li>
        <li>English words to find {langName} translations</li>
        <li>Word forms and dictionary forms (lemmas)</li>
    </ul>
</div>
```

#### 4.2: Create FoundResult Component

```svelte
<!-- src/lib/components/search/FoundResult.svelte -->
<script lang="ts">
    import type { FoundResult } from '$lib/types/search';
    
    export let result: FoundResult;
    
    const { wordform_metadata, lemma_metadata } = result.data;
</script>

<div class="found-result">
    <h2>{wordform_metadata.wordform}</h2>
    
    <div class="wordform-details">
        <p>
            <strong>Translation:</strong> 
            {wordform_metadata.translations?.join('; ') || 'No translation available'}
        </p>
        
        <p>
            <strong>Part of Speech:</strong> 
            {wordform_metadata.part_of_speech || 'Unknown'}
        </p>
        
        <p>
            <strong>Form Type:</strong> 
            {wordform_metadata.inflection_type || 'Unknown'}
        </p>
        
        <p>
            <strong>Dictionary Form (Lemma):</strong> 
            {#if wordform_metadata.lemma}
                <a href="/{result.target_language_code}/lemma/{wordform_metadata.lemma}">
                    {wordform_metadata.lemma}
                </a>
            {:else}
                <em>No lemma linked</em>
            {/if}
        </p>
        
        {#if wordform_metadata.possible_misspellings}
            <p>
                <strong>Possible Misspellings:</strong> 
                {wordform_metadata.possible_misspellings.join(', ')}
            </p>
        {/if}
    </div>
    
    <a href="/{result.target_language_code}/wordform/{wordform_metadata.wordform}" class="view-details">
        View full details
    </a>
</div>
```

#### 4.3: Create MultipleMatches Component

```svelte
<!-- src/lib/components/search/MultipleMatches.svelte -->
<script lang="ts">
    import type { MultipleMatchesResult } from '$lib/types/search';
    
    export let result: MultipleMatchesResult;
    
    const { target_language_results, english_results } = result.data;
    const hasTargetMatches = target_language_results.matches?.length > 0;
    const hasEnglishMatches = english_results.matches?.length > 0;
    const hasTargetMisspellings = target_language_results.possible_misspellings?.length > 0;
    const hasEnglishMisspellings = english_results.possible_misspellings?.length > 0;
</script>

<div class="multiple-matches">
    <h2>Search Results for "{result.query}"</h2>
    
    {#if hasTargetMatches}
        <div class="result-section">
            <h3>{result.target_language_name} Matches</h3>
            <ul class="results-list">
                {#each target_language_results.matches as match}
                    <li>
                        <div class="match-item">
                            <div class="match-word">
                                <a href="/{result.target_language_code}/wordform/{match.target_language_wordform}">
                                    {match.target_language_wordform}
                                </a>
                                <span class="pos-tag">{match.part_of_speech}</span>
                                <span class="inflection-tag">{match.inflection_type}</span>
                            </div>
                            
                            <div class="match-details">
                                {#if match.target_language_lemma !== match.target_language_wordform}
                                    <div class="lemma-link">
                                        <strong>Lemma:</strong> 
                                        <a href="/{result.target_language_code}/lemma/{match.target_language_lemma}">
                                            {match.target_language_lemma}
                                        </a>
                                    </div>
                                {/if}
                                
                                <div class="translations">
                                    {match.english.join(', ')}
                                </div>
                            </div>
                        </div>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
    
    {#if hasEnglishMatches}
        <div class="result-section">
            <h3>{result.target_language_name} words matching English term "{result.query}"</h3>
            <ul class="results-list">
                {#each english_results.matches as match}
                    <li>
                        <div class="match-item">
                            <div class="match-word">
                                <a href="/{result.target_language_code}/wordform/{match.target_language_wordform}">
                                    {match.target_language_wordform}
                                </a>
                                <span class="pos-tag">{match.part_of_speech}</span>
                                <span class="inflection-tag">{match.inflection_type}</span>
                            </div>
                            
                            <div class="match-details">
                                {#if match.target_language_lemma !== match.target_language_wordform}
                                    <div class="lemma-link">
                                        <strong>Lemma:</strong> 
                                        <a href="/{result.target_language_code}/lemma/{match.target_language_lemma}">
                                            {match.target_language_lemma}
                                        </a>
                                    </div>
                                {/if}
                                
                                <div class="translations">
                                    {match.english.join(', ')}
                                </div>
                            </div>
                        </div>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
    
    {#if hasTargetMisspellings}
        <div class="result-section suggestions">
            <h3>Did you mean one of these?</h3>
            <ul class="suggestion-list">
                {#each target_language_results.possible_misspellings as suggestion}
                    <li>
                        <a href="/{result.target_language_code}/search?q={encodeURIComponent(suggestion)}">
                            {suggestion}
                        </a>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
    
    {#if hasEnglishMisspellings}
        <div class="result-section suggestions">
            <h3>Did you mean one of these English words?</h3>
            <ul class="suggestion-list">
                {#each english_results.possible_misspellings as suggestion}
                    <li>
                        <a href="/{result.target_language_code}/search?q={encodeURIComponent(suggestion)}">
                            {suggestion}
                        </a>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
    
    {#if !hasTargetMatches && !hasEnglishMatches && !hasTargetMisspellings && !hasEnglishMisspellings}
        <div class="no-results">
            <p>No results found for "{result.query}".</p>
        </div>
    {/if}
</div>
```

#### 4.4: Create InvalidResult Component

```svelte
<!-- src/lib/components/search/InvalidResult.svelte -->
<script lang="ts">
    import type { InvalidResult } from '$lib/types/search';
    
    export let result: InvalidResult;
    
    const hasSuggestions = result.data.possible_misspellings?.length > 0;
</script>

<div class="invalid-result">
    <h2>No Results Found</h2>
    <p>"{result.data.wordform}" did not match any words in {result.target_language_name} or English translations.</p>
    
    {#if hasSuggestions}
        <div class="suggestions">
            <h3>Did you mean:</h3>
            <ul class="suggestion-list">
                {#each result.data.possible_misspellings as suggestion}
                    <li>
                        <a href="/{result.target_language_code}/search?q={encodeURIComponent(suggestion)}">
                            {suggestion}
                        </a>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
    
    <div class="search-again">
        <p>Try another search term or check your spelling.</p>
    </div>
</div>
```

#### 4.5: Create ErrorResult Component

```svelte
<!-- src/lib/components/search/ErrorResult.svelte -->
<script lang="ts">
    import type { ErrorResult } from '$lib/types/search';
    
    export let result: ErrorResult;
</script>

<div class="error-result">
    <h2>Search Error</h2>
    <p>Sorry, we encountered an error processing your search.</p>
    <p class="error-message">{result.error}</p>
    <p>Please try again later or with a different search term.</p>
</div>
```

#### 4.6: Create SearchResults Component

```svelte
<!-- src/lib/components/search/SearchResults.svelte -->
<script lang="ts">
    import type { SearchResult } from '$lib/types/search';
    import EmptyState from './EmptyState.svelte';
    import FoundResult from './FoundResult.svelte';
    import MultipleMatches from './MultipleMatches.svelte';
    import InvalidResult from './InvalidResult.svelte';
    import ErrorResult from './ErrorResult.svelte';
    
    export let result: SearchResult;
    export let langName: string;
</script>

<div class="search-results">
    {#if result.status === 'empty_query'}
        <EmptyState {langName} />
    {:else if result.status === 'found'}
        <FoundResult {result} />
    {:else if result.status === 'multiple_matches'}
        <MultipleMatches {result} />
    {:else if result.status === 'invalid'}
        <InvalidResult {result} />
    {:else if result.status === 'error'}
        <ErrorResult {result} />
    {:else}
        <div class="unknown-status">
            <p>Unknown search result status: {result.status}</p>
        </div>
    {/if}
</div>
```

#### 4.7: Update Search Page with Components

```svelte
<!-- src/routes/[lang]/search/+page.svelte -->
<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { searchWord } from '$lib/services/api';
    import SearchResults from '$lib/components/search/SearchResults.svelte';
    import type { SearchResult } from '$lib/types/search';
    
    export let data; // From load function
    
    let query = $page.url.searchParams.get('q') || '';
    let result: SearchResult | null = null;
    let loading = false;
    
    async function handleSearch() {
        if (!query.trim()) {
            result = {
                status: 'empty_query',
                query: '',
                target_language_code: data.lang,
                target_language_name: data.langName,
                data: {}
            };
            return;
        }
        
        loading = true;
        
        // Update URL to reflect search
        goto(`/${data.lang}/search?q=${encodeURIComponent(query)}`, { 
            replaceState: true,
            keepFocus: true,
            noScroll: true
        });
        
        result = await searchWord(data.lang, query);
        loading = false;
        
        // Handle immediate redirects for exact matches
        if (result.status === 'redirect') {
            goto(`/${data.lang}/wordform/${result.data.redirect_to}`);
        }
    }
    
    // Perform search on initial load if query exists
    if (query && !result) {
        handleSearch();
    } else if (!query) {
        // If no query, show empty state
        result = {
            status: 'empty_query',
            query: '',
            target_language_code: data.lang,
            target_language_name: data.langName,
            data: {}
        };
    }
</script>

<svelte:head>
    <title>
        {query 
            ? `Search results for "${query}" - ${data.langName}`
            : `Search ${data.langName}`}
    </title>
</svelte:head>

<div class="container">
    <h1>Search {data.langName} Words</h1>
    
    <form on:submit|preventDefault={handleSearch}>
        <div class="search-field">
            <input 
                type="text" 
                bind:value={query} 
                placeholder="Enter a word to search..."
                aria-label="Search term"
            >
            <button type="submit" disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>
        </div>
    </form>
    
    {#if loading}
        <div class="loading">Searching...</div>
    {:else if result}
        <SearchResults {result} langName={data.langName} />
    {/if}
</div>

<style>
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .search-field {
        display: flex;
        margin-bottom: 2rem;
    }
    
    input {
        flex: 1;
        padding: 0.5rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px 0 0 4px;
    }
    
    button {
        padding: 0.5rem 1rem;
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 0 4px 4px 0;
        cursor: pointer;
    }
    
    button:disabled {
        background-color: #999;
        cursor: not-allowed;
    }
    
    .loading {
        text-align: center;
        padding: 2rem;
        font-style: italic;
    }
</style>
```

### Stage 5: Integrate with SSR Load Function

#### 5.1: Update Page Server Load Function

To ensure the search results are available on initial server render for SEO:

```typescript
// src/routes/[lang]/search/+page.server.ts
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getLanguageName } from '$lib/utils/languages';

export const load = (async ({ params, url, fetch }) => {
    const { lang } = params;
    const q = url.searchParams.get('q') || '';
    
    const langName = getLanguageName(lang);
    if (!langName) {
        throw error(404, `Language '${lang}' not found`);
    }
    
    // Only fetch initial search results if there's a query
    let initialResult = null;
    if (q) {
        try {
            const response = await fetch(
                `/api/lang/${lang}/unified_search?q=${encodeURIComponent(q)}`
            );
            
            if (response.ok) {
                initialResult = await response.json();
                
                // Handle redirect case at the server level
                if (initialResult.status === 'redirect') {
                    return {
                        redirect: `/${lang}/wordform/${initialResult.data.redirect_to}`
                    };
                }
            }
        } catch (err) {
            console.error('Server-side search error:', err);
            // Let the client handle the error case
        }
    }
    
    return {
        lang,
        langName,
        query: q,
        initialResult
    };
}) satisfies PageServerLoad;
```

#### 5.2: Update Page Component to Use Server Load Data

```svelte
<!-- src/routes/[lang]/search/+page.svelte -->
<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { searchWord } from '$lib/services/api';
    import SearchResults from '$lib/components/search/SearchResults.svelte';
    import type { SearchResult } from '$lib/types/search';
    
    export let data; // From load function
    
    let query = data.query || '';
    let result: SearchResult | null = data.initialResult || null;
    let loading = false;
    
    async function handleSearch() {
        if (!query.trim()) {
            result = {
                status: 'empty_query',
                query: '',
                target_language_code: data.lang,
                target_language_name: data.langName,
                data: {}
            };
            return;
        }
        
        loading = true;
        
        // Update URL to reflect search
        goto(`/${data.lang}/search?q=${encodeURIComponent(query)}`, { 
            replaceState: true,
            keepFocus: true,
            noScroll: true
        });
        
        result = await searchWord(data.lang, query);
        loading = false;
        
        // Handle immediate redirects for exact matches
        if (result.status === 'redirect') {
            goto(`/${data.lang}/wordform/${result.data.redirect_to}`);
        }
    }
    
    // If no result and no query, show empty state
    if (!result && !query) {
        result = {
            status: 'empty_query',
            query: '',
            target_language_code: data.lang,
            target_language_name: data.langName,
            data: {}
        };
    }
</script>

<!-- Rest of component same as before -->
```

### Stage 6: Add Global Search Component

#### 6.1: Create Reusable Search Component

```svelte
<!-- src/lib/components/GlobalSearch.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    
    export let lang: string;
    export let mini = false; // For compact display in header
    
    let query = '';
    
    function handleSearch() {
        if (!query.trim()) return;
        goto(`/${lang}/search?q=${encodeURIComponent(query)}`);
    }
</script>

<form 
    on:submit|preventDefault={handleSearch}
    class:mini
>
    <div class="search-field">
        <input 
            type="text" 
            bind:value={query} 
            placeholder={mini ? "Search..." : "Search for a word..."}
            aria-label="Search term"
        >
        <button type="submit">
            <span class="icon">🔍</span>
            {#if !mini}
                <span class="text">Search</span>
            {/if}
        </button>
    </div>
</form>

<style>
    form {
        width: 100%;
        max-width: 500px;
    }
    
    form.mini {
        max-width: 200px;
    }
    
    .search-field {
        display: flex;
        width: 100%;
    }
    
    input {
        flex: 1;
        padding: 0.5rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px 0 0 4px;
        min-width: 0; /* Allows flex shrinking */
    }
    
    button {
        padding: 0.5rem 1rem;
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 0 4px 4px 0;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .mini button {
        padding: 0.5rem;
    }
</style>
```

#### 6.2: Add to App Header

```svelte
<!-- src/lib/components/Header.svelte -->
<script lang="ts">
    import { page } from '$app/stores';
    import GlobalSearch from './GlobalSearch.svelte';
    
    // Extract language from current path
    $: lang = $page.params.lang || 'el'; // Default to Greek if not in URL
</script>

<header>
    <div class="logo">
        <a href="/">Hello Zenno</a>
    </div>
    
    <nav>
        <ul>
            <li>
                <a href="/languages">Languages</a>
            </li>
            <!-- Other navigation items -->
        </ul>
    </nav>
    
    <div class="search">
        <GlobalSearch {lang} mini={true} />
    </div>
</header>

<style>
    header {
        display: flex;
        align-items: center;
        padding: 1rem;
        background-color: #f5f5f5;
        border-bottom: 1px solid #ddd;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    nav {
        margin: 0 auto;
    }
    
    ul {
        display: flex;
        list-style: none;
        gap: 1.5rem;
        margin: 0;
        padding: 0;
    }
    
    .search {
        margin-left: auto;
    }
</style>
```

### Stage 7: Add Search History Store

#### 7.1: Create Search History Store

```typescript
// src/lib/stores/searchHistory.ts
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Define the structure of a search history item
interface SearchHistoryItem {
    query: string;
    lang: string;
    timestamp: number;
}

// Maximum number of items to store
const MAX_HISTORY_ITEMS = 10;

// Create a writable store with initial value from localStorage if available
function createSearchHistoryStore() {
    // Initialize from localStorage if in browser
    const initialValue: SearchHistoryItem[] = browser 
        ? JSON.parse(localStorage.getItem('searchHistory') || '[]')
        : [];
    
    const { subscribe, update } = writable<SearchHistoryItem[]>(initialValue);
    
    return {
        subscribe,
        
        // Add a search to history
        addSearch: (query: string, lang: string) => {
            update(items => {
                // Remove any existing identical searches
                const filtered = items.filter(item => 
                    !(item.query === query && item.lang === lang)
                );
                
                // Add new search at the beginning
                const newItems = [
                    { query, lang, timestamp: Date.now() },
                    ...filtered
                ].slice(0, MAX_HISTORY_ITEMS);
                
                // Save to localStorage if in browser
                if (browser) {
                    localStorage.setItem('searchHistory', JSON.stringify(newItems));
                }
                
                return newItems;
            });
        },
        
        // Clear search history
        clear: () => {
            update(() => {
                // Clear localStorage if in browser
                if (browser) {
                    localStorage.removeItem('searchHistory');
                }
                return [];
            });
        }
    };
}

export const searchHistory = createSearchHistoryStore();
```

#### 7.2: Update Search Page to Use History

```svelte
<!-- src/routes/[lang]/search/+page.svelte -->
<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { searchWord } from '$lib/services/api';
    import { searchHistory } from '$lib/stores/searchHistory';
    import SearchResults from '$lib/components/search/SearchResults.svelte';
    import type { SearchResult } from '$lib/types/search';
    
    export let data; // From load function
    
    let query = data.query || '';
    let result: SearchResult | null = data.initialResult || null;
    let loading = false;
    
    async function handleSearch() {
        if (!query.trim()) {
            result = {
                status: 'empty_query',
                query: '',
                target_language_code: data.lang,
                target_language_name: data.langName,
                data: {}
            };
            return;
        }
        
        loading = true;
        
        // Update URL to reflect search
        goto(`/${data.lang}/search?q=${encodeURIComponent(query)}`, { 
            replaceState: true,
            keepFocus: true,
            noScroll: true
        });
        
        result = await searchWord(data.lang, query);
        loading = false;
        
        // Add to search history if successful and status is not error
        if (result.status !== 'error' && result.status !== 'empty_query') {
            searchHistory.addSearch(query, data.lang);
        }
        
        // Handle immediate redirects for exact matches
        if (result.status === 'redirect') {
            goto(`/${data.lang}/wordform/${result.data.redirect_to}`);
        }
    }
    
    // If no result and no query, show empty state
    if (!result && !query) {
        result = {
            status: 'empty_query',
            query: '',
            target_language_code: data.lang,
            target_language_name: data.langName,
            data: {}
        };
    }
</script>

<!-- Rest of component -->
```

#### 7.3: Create Search History Component

```svelte
<!-- src/lib/components/search/SearchHistory.svelte -->
<script lang="ts">
    import { searchHistory } from '$lib/stores/searchHistory';
    
    export let currentLang: string;
    export let onSelectQuery: (query: string) => void;
    
    // Filter history to show current language first, then others
    $: filteredHistory = $searchHistory
        .sort((a, b) => {
            // First sort by language (current lang first)
            if (a.lang === currentLang && b.lang !== currentLang) return -1;
            if (a.lang !== currentLang && b.lang === currentLang) return 1;
            // Then sort by timestamp (newest first)
            return b.timestamp - a.timestamp;
        });
        
    function handleClearHistory() {
        if (confirm('Are you sure you want to clear your search history?')) {
            searchHistory.clear();
        }
    }
</script>

{#if filteredHistory.length > 0}
    <div class="search-history">
        <div class="history-header">
            <h3>Recent Searches</h3>
            <button 
                type="button" 
                class="clear-btn" 
                on:click={handleClearHistory}
            >
                Clear
            </button>
        </div>
        
        <ul class="history-list">
            {#each filteredHistory as item}
                <li>
                    <button 
                        type="button"
                        class="history-item"
                        on:click={() => onSelectQuery(item.query)}
                    >
                        <span class="query">{item.query}</span>
                        <span class="lang-tag">{item.lang}</span>
                    </button>
                </li>
            {/each}
        </ul>
    </div>
{/if}

<style>
    .search-history {
        margin-top: 2rem;
        border-top: 1px solid #eee;
        padding-top: 1rem;
    }
    
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1rem;
        margin: 0;
    }
    
    .clear-btn {
        background: none;
        border: none;
        color: #666;
        font-size: 0.85rem;
        cursor: pointer;
        text-decoration: underline;
    }
    
    .history-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .history-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        padding: 0.5rem;
        text-align: left;
        background: none;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .history-item:hover {
        background-color: #f5f5f5;
    }
    
    .lang-tag {
        font-size: 0.75rem;
        background-color: #eee;
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
    }
</style>
```

#### 7.4: Add Search History to Search Page

```svelte
<!-- Update src/routes/[lang]/search/+page.svelte -->
<script>
    // ... existing imports
    import SearchHistory from '$lib/components/search/SearchHistory.svelte';
    
    // ... existing code
    
    function selectFromHistory(historyQuery) {
        query = historyQuery;
        handleSearch();
    }
</script>

<div class="container">
    <!-- ... existing search form -->
    
    {#if loading}
        <div class="loading">Searching...</div>
    {:else if result}
        <SearchResults {result} langName={data.langName} />
    {/if}
    
    {#if result?.status === 'empty_query'}
        <SearchHistory 
            currentLang={data.lang} 
            onSelectQuery={selectFromHistory} 
        />
    {/if}
</div>
```

## Testing Recommendations

After implementing each stage, test thoroughly:

1. **Backend API Testing**:
   - Test all search scenarios: lemma, wordform, English word, misspelling, invalid input
   - Verify the API returns the correct data structure for each case
   - Check error handling for edge cases

2. **Frontend Component Testing**:
   - Test rendering of each component with mock data
   - Verify state management and transitions
   - Test user interactions for each search scenario

3. **Integration Testing**:
   - Test the complete user journey from search to result display
   - Verify that redirects work correctly for exact matches
   - Test SSR functionality for initial page load
   - Verify that search history functionality works correctly

## Next Steps

Once the basic functionality is working, consider these future enhancements:

1. **Performance Optimization**:
   - Implement caching for common searches
   - Add lazy loading for search history

2. **User Experience Improvements**:
   - Add keyboard shortcuts
   - Implement search suggestions
   - Add voice search capability

3. **Advanced Features**:
   - Support for multiple language search
   - Advanced search filters
   - Integration with user's learning progress

This plan provides a detailed, step-by-step approach to implementing a unified search API in SvelteKit. By following these stages, you'll create a clean, maintainable, and user-friendly search experience that leverages the power of the existing backend while providing a more modern frontend interface.
