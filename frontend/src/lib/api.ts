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

/**
 * Custom error class for API errors with status and body
 */
export class ApiError extends Error {
    status: number;
    body: Record<string, unknown>;
    
    constructor(message: string, status: number, body: Record<string, unknown> = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.body = body;
    }
}
import { resolveRoute, RouteName, type RouteParams } from "./generated/routes";
import { API_BASE_URL } from "./config";

import type { SupabaseClient } from '@supabase/supabase-js'; // Import type

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
 * @param supabaseClient Optional Supabase client instance (required for SSR calls from load functions)
 * @param routeName Name of the route from RouteName enum
 * @param params Parameters required for the route
 * @param options Fetch options
 * @param timeoutMs Optional timeout in milliseconds (default: 30000)
 * @returns The JSON response
 */
export async function apiFetch<T extends RouteName, R = any>({
    supabaseClient, // Make optional again for flexibility
    routeName,
    params,
    options = {},
    timeoutMs = 30000, // Default 30 second timeout
    searchParams,
}: {
    supabaseClient?: SupabaseClient | null; // Allow optional/null
    routeName: T;
    params: RouteParams[T];
    options?: RequestInit;
    timeoutMs?: number;
    searchParams?: Record<string, string | number | boolean | undefined>;
}): Promise<R> {
    let url = getApiUrl(routeName, params);
    if (searchParams && Object.keys(searchParams).length > 0) {
        const usp = new URLSearchParams();
        Object.entries(searchParams).forEach(([k, v]) => {
            if (v !== undefined && v !== null && v !== "") {
                usp.append(k, String(v));
            }
        });
        const qs = usp.toString();
        if (qs) {
            url = `${url}?${qs}`;
        }
    }
    if (import.meta.env.DEV) console.log(`[apiFetch] Requesting URL: ${url}`);
    
    // Use the passed supabaseClient. It might be null or undefined.
    const headers = new Headers(options.headers);
    
    // Only try to get session if we have a non-null client instance
    if (supabaseClient) {
      try {
        let {
          data: { session },
        } = await supabaseClient.auth.getSession();

        // If the session is about to expire (or already expired), refresh it server-side
        if (
          session?.expires_at &&
          session.expires_at * 1000 < Date.now() + 60 * 1000 // < 1 min buffer
        ) {
          const { data, error } = await supabaseClient.auth.refreshSession();
          if (error) {
            console.warn('Supabase refreshSession error:', error.message);
          }
          session = data.session ?? session; // fall back to old session if refresh failed
        }

        if (session?.access_token) {
          // Trim any whitespace or newlines from the token
          const cleanToken = session.access_token.trim();
          headers.set('Authorization', `Bearer ${cleanToken}`);
        }
      } catch (sessionError) {
        console.warn('Error preparing auth token:', sessionError);
        // Continue without auth token
      }
    }
    // Ensure Content-Type is set if not already present (optional, good practice for POST/PUT)
    // if (!headers.has('Content-Type') && (options.method === 'POST' || options.method === 'PUT')) {
    //     headers.set('Content-Type', 'application/json');
    // }

    const fetchOptions: RequestInit = {
        ...options,
        headers: headers, // Use the modified headers
    };
    // --- END CHANGE ---    

    // Use a timeout to ensure we wait long enough for operations like wordform generation
    const fetchPromise = fetch(url, fetchOptions);
    
    let timeoutId: ReturnType<typeof setTimeout>;
    const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutId = setTimeout(() => {
            if (import.meta.env.DEV) console.warn(`[apiFetch] Request to ${url} timed out after ${timeoutMs}ms.`);
            reject(new Error('API request timed out'));
        }, timeoutMs);
    });
    
    // Race the fetch against the timeout
    let response: Response;
    try {
        response = await Promise.race([fetchPromise, timeoutPromise]) as Response;
        clearTimeout(timeoutId!);
    } catch (e) {
        clearTimeout(timeoutId!);
        if (import.meta.env.DEV) console.error(`[apiFetch] Error during fetch for ${url}:`, e);
        throw e;
    }

    if (import.meta.env.DEV) console.log(`[apiFetch] Response status for ${url}: ${response.status}`);

    if (!response.ok) {
        let errorData: Record<string, unknown> = {};
        try {
            errorData = await response.json();
        } catch {
            // Ignore if response body is not JSON
        }
        const description = typeof errorData?.description === 'string' ? errorData.description : undefined;
        const errorMessage = typeof errorData?.message === 'string' ? errorData.message : undefined;
        const message = description || errorMessage || `API request failed: ${response.status}`;
        throw new ApiError(message, response.status, errorData);        
    }

    // Handle status codes that typically have empty bodies
    if (response.status === 204 || response.status === 205 || response.status === 304) {
        return {} as R; // Return empty object for empty responses
    }
    
    // Check if response has content before trying to parse as JSON
    const contentLength = response.headers.get('content-length');
    const contentType = response.headers.get('content-type');
    const hasEmptyBody = contentLength === '0' || (contentLength === null && !contentType?.includes('json'));

    if (import.meta.env.DEV) console.log(`[apiFetch] Response for ${url} - Content-Length: ${contentLength}, Content-Type: ${contentType}, HasEmptyBody: ${hasEmptyBody}`);

    if (hasEmptyBody) {
        if (import.meta.env.DEV) console.log(`[apiFetch] Returning empty object for ${url} due to empty body.`);
        return {} as R;
    }
    
    try {
        const jsonData = await response.json();
        if (import.meta.env.DEV) console.log(`[apiFetch] Returning JSON data for ${url}.`);
        return jsonData;
    } catch (jsonError) {
        if (import.meta.env.DEV) console.error(`[apiFetch] Error parsing JSON for ${url}:`, jsonError);
        return {} as R;
    }
}

/**
 * Fetch all available languages
 * 
 * @deprecated Use `getLanguages` from `language-utils.ts` instead which uses static data
 */
export async function getLanguages(supabaseClient?: SupabaseClient | null) {
    // Import here to avoid circular dependencies
    const { getLanguages: getStaticLanguages } = await import('./language-utils');
    
    // Use the static data instead of making an API call
    return getStaticLanguages();
}

/**
 * Fetch a sentence by language code and slug
 */
export async function getSentence(supabaseClient: SupabaseClient | null, target_language_code: string, slug: string) {
    return apiFetch({ 
        supabaseClient,
        routeName: RouteName.SENTENCE_API_GET_SENTENCE_BY_SLUG_API, 
        params: { target_language_code, slug } 
    });
}

/**
 * Fetch all sentences for a language
 */
export async function getSentencesForLanguage(supabaseClient: SupabaseClient | null, target_language_code: string) {
    return apiFetch({ 
        supabaseClient,
        routeName: RouteName.SENTENCE_API_SENTENCES_LIST_API, 
        params: { target_language_code } 
    });
}

/**
 * Fetch all lemmas for a language
 */
export async function getLemmasForLanguage(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    sort: string = "alpha", // Sort param likely needs adding to API/RouteParams if used
) {
    return apiFetch({ 
        supabaseClient,
        routeName: RouteName.LEMMA_API_LEMMAS_LIST_API, 
        params: { target_language_code }, // Add sort param if needed
        options: {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        } 
    });
}

/**
 * Fetch all phrases for a language
 */
export async function getPhrasesForLanguage(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    sort: string = "alpha", // Sort param likely needs adding to API/RouteParams if used
) {
    return apiFetch({ 
        supabaseClient,
        routeName: RouteName.PHRASE_API_PHRASES_LIST_API, 
        params: { target_language_code }, // Add sort param if needed
        options: {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        } 
    });
}

/**
 * Fetch all wordforms for a language
 */
export async function getWordformsForLanguage(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    sort: string = "alpha", // Sort param likely needs adding to API/RouteParams if used
) {
    return apiFetch({ 
        supabaseClient,
        routeName: RouteName.WORDFORM_API_WORDFORMS_LIST_API, 
        params: { target_language_code }, // Add sort param if needed
        options: {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        } 
    });
}

/**
 * Get search landing page data
 */
export async function getSearchLandingData(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    query?: string, // Query param not used in API call currently
) {
    const response = await apiFetch({
        supabaseClient,
        routeName: RouteName.SEARCH_API_SEARCH_LANDING_API,
        params: { target_language_code },
        options: {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        }
    });
    return response;
}

/**
 * Search for a word in a language using the search API
 * (Simple redirect method - DEPRECATED, use unifiedSearch instead)
 */
export async function searchWord(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    wordform: string,
) {
    return apiFetch({
        supabaseClient,
        routeName: RouteName.SEARCH_API_SEARCH_WORD_API,
        params: { target_language_code, wordform },
        options: {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        }
    });
}

/**
 * Search for a word using the unified search API
 * 
 * @param supabaseClient Supabase client instance
 * @param langCode Language code (e.g. 'el')
 * @param query Search query
 * @returns Search results
 */
export async function unifiedSearch(
    supabaseClient: SupabaseClient | null,
    langCode: string, 
    query: string
): Promise<SearchResult> {
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
        // unified_search might not be in RouteName, construct URL manually
        const url = `${API_BASE_URL}/api/lang/${langCode}/unified_search?q=${encodeURIComponent(query)}`;
        
        // Use the passed supabaseClient to get the token
        const headers = new Headers();
        
        if (supabaseClient) {
            try {
                // Get session from the passed client to extract the token
                const { data: { session } } = await supabaseClient.auth.getSession(); 
                // Note: While this still calls getSession, it uses the potentially validated 
                // client instance passed from the load function. The warning might still appear 
                // here, but it aligns the pattern with apiFetch.
                if (session?.access_token) {
                    // Trim any whitespace or newlines from the token
                    const cleanToken = session.access_token.trim();
                    headers.set('Authorization', `Bearer ${cleanToken}`);
                }
            } catch (sessionError) {
                console.warn('Error getting session in unifiedSearch:', sessionError);
                // Continue without auth token
            }
        }

        const response = await fetch(url, { headers });
        
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
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    wordform: string,
    accessToken?: string | null,
) {
    try {
        // Use the type-safe API fetch to get wordform metadata with a longer timeout
        // since wordform generation can take time
        const result = await apiFetch({
            supabaseClient,
            routeName: RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API,
            params: { target_language_code, wordform },
            options: {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
                },
            },
            timeoutMs: 60000, // 60 second timeout to allow for synchronous wordform generation
        });
        return result;
    } catch (error: unknown) {
        console.error(`API: Error fetching wordform ${wordform}:`, error);
        // For 401 and 404, rethrow so loaders can handle (redirect or show error page)
        if (error instanceof ApiError && (error.status === 401 || error.status === 404)) {
            throw error;
        }
        // Re-throw other errors
        throw error;
    }
}

/**
 * Get lemma metadata.
 * This function handles potential 401 errors if generation is required but user is not logged in.
 */
export async function getLemmaMetadata(
    supabaseClient: SupabaseClient | null,
    target_language_code: string,
    lemma: string
) {
    try {
        // Use the type-safe API fetch to get lemma metadata with a longer timeout
        // since lemma generation can take time
        const result = await apiFetch({
            supabaseClient,
            routeName: RouteName.LEMMA_API_GET_LEMMA_METADATA_API, 
            params: { target_language_code, lemma },
            options: {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            },
            timeoutMs: 60000, // 60 seconds
        });
        return result;
    } catch (error: unknown) {
        console.error(`API: Error fetching lemma ${lemma}:`, error);
        // Specifically handle the 401 case where generation requires login
        if (error instanceof ApiError) {
            if (error.status === 401 && error.body?.authentication_required_for_generation) {
                console.warn(`API: Authentication required to generate lemma ${lemma}`);
                // Return the error body which contains partial data and the flag
                return error.body;
            } else if (error.status === 404) {
                console.warn(`API: Lemma ${lemma} not found (404).`);
                // Return the error body which contains the 404 details
                return error.body;
            }
        }
        // Re-throw other errors
        throw error; 
    }
}

if (!API_BASE_URL) {
    throw new Error('API_BASE_URL is undefined. In production, check that VITE_API_URL is set in environment variables.');
}
