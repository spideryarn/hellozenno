/**
 * API utility for communicating with the Flask backend
 */

import type {
    Language,
    Lemma,
    Phrase,
    Sentence,
    SentenceMetadata,
    Wordform,
    SearchResult,
} from "./types";
import { resolveRoute, RouteName, type RouteParams } from "./generated/routes";
import { API_BASE_URL } from "./config";

/**
 * Type-safe way to build URLs using the route mapping
 *
 * @param routeName Name of the route from RouteName enum
 * @param params Parameters required for the route
 * @returns The full URL including the API base
 */
export function getApiUrl<T extends RouteName>(
    routeName: T,
    params: RouteParams[T],
): string {
    const routePath = resolveRoute(routeName, params);
    return `${API_BASE_URL}${routePath}`;
}

/**
 * Type-safe API fetch function
 *
 * @param routeName Name of the route from RouteName enum
 * @param params Parameters required for the route
 * @param options Fetch options
 * @param timeoutMs Optional timeout in milliseconds (default: 30000)
 * @returns The JSON response
 */
export async function apiFetch<T extends RouteName, R = any>(
    routeName: T,
    params: RouteParams[T],
    options: RequestInit = {},
    timeoutMs: number = 30000, // Default 30 second timeout
): Promise<R> {
    const url = getApiUrl(routeName, params);
    
    // Use a timeout to ensure we wait long enough for operations like wordform generation
    const fetchPromise = fetch(url, options);
    
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('API request timed out')), timeoutMs);
    });
    
    // Race the fetch against the timeout
    const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            errorData.description ||
                `API request failed: ${response.status}`,
        );
    }

    return response.json();
}

/**
 * Fetch all available languages
 */
export async function getLanguages() {
    return apiFetch(RouteName.LANGUAGES_API_GET_LANGUAGES_API, {});
}

/**
 * Fetch a sentence by language code and slug
 */
export async function getSentence(target_language_code: string, slug: string) {
    return apiFetch(RouteName.SENTENCE_API_GET_SENTENCE_BY_SLUG_API, {
        target_language_code,
        slug,
    });
}

/**
 * Fetch all sentences for a language
 */
export async function getSentencesForLanguage(target_language_code: string) {
    return apiFetch(RouteName.SENTENCE_API_SENTENCES_LIST_API, {
        target_language_code,
    });
}

/**
 * Fetch all lemmas for a language
 */
export async function getLemmasForLanguage(
    target_language_code: string,
    sort: string = "alpha",
) {
    return apiFetch(RouteName.LEMMA_API_LEMMAS_LIST_API, {
        target_language_code,
    }, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    });
}

/**
 * Fetch all phrases for a language
 */
export async function getPhrasesForLanguage(
    target_language_code: string,
    sort: string = "alpha",
) {
    return apiFetch(RouteName.PHRASE_API_PHRASES_LIST_API, {
        target_language_code,
    }, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    });
}

/**
 * Fetch all wordforms for a language
 */
export async function getWordformsForLanguage(
    target_language_code: string,
    sort: string = "alpha",
) {
    return apiFetch(RouteName.WORDFORM_API_WORDFORMS_LIST_API, {
        target_language_code,
    }, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    });
}

/**
 * Get search landing page data
 */
export async function getSearchLandingData(
    target_language_code: string,
    query?: string,
) {
    // Use the type-safe API fetch with RouteName
    const response = await apiFetch(
        RouteName.SEARCH_API_SEARCH_LANDING_API,
        { target_language_code },
        {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        },
    );

    // If there's a query parameter, we need to add it to the URL
    // This could be enhanced by extending the route params type to include optional query params
    if (query) {
        // Add query parameters if needed
        // Note: This isn't needed for the current implementation
        // but kept here as example for handling query params
    }

    return response;
}

/**
 * Search for a word in a language using the search API
 * (Simple redirect method - DEPRECATED, use unifiedSearch instead)
 */
export async function searchWord(
    target_language_code: string,
    wordform: string,
) {
    // Use the type-safe API fetch with RouteName
    return apiFetch(
        RouteName.SEARCH_API_SEARCH_WORD_API,
        { target_language_code, wordform },
        {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        },
    );
}

/**
 * Search for a word using the unified search API
 * 
 * @param langCode Language code (e.g. 'el')
 * @param query Search query
 * @returns Search results
 */
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
        // Use apiFetch for type-safe API access, but handle 'unified_search' specifically
        // since it might not be in the routes yet
        const url = `${API_BASE_URL}/api/lang/${langCode}/unified_search?q=${encodeURIComponent(query)}`;
        
        const response = await fetch(url);
        
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

/**
 * Get wordform metadata with enhanced search capabilities
 * 
 * This API will:
 * - Return wordform data if found
 * - Search for similar words if not found
 * - Return search results for multiple matches
 * - Handle English translation search
 */
export async function getWordformWithSearch(
    target_language_code: string,
    wordform: string,
) {
    try {
        console.log(`API: Fetching wordform ${wordform} in ${target_language_code}`);
        // Use the type-safe API fetch to get wordform metadata with a longer timeout
        // since wordform generation can take time
        const result = await apiFetch(
            RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API,
            { target_language_code, wordform },
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            },
            90000, // 90 second timeout to allow for synchronous wordform generation
        );
        console.log(`API: Received result for ${wordform}:`, result);
        return result;
    } catch (error) {
        console.error(`API: Error fetching wordform ${wordform}:`, error);
        // For 404 errors, return the error response
        // This allows us to handle "invalid word" cases with proper data
        if (error instanceof Error && error.message.includes('404')) {
            console.log(`API: Got 404 for ${wordform}, trying again to get error details`);
            const response = await fetch(
                getApiUrl(RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API, 
                    { target_language_code, wordform }
                ),
                {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                }
            );
            const errorData = await response.json();
            console.log(`API: Received error data for ${wordform}:`, errorData);
            return errorData;
        }
        throw error;
    }
}
