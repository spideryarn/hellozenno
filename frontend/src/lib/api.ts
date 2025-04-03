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
 * @returns The JSON response
 */
export async function apiFetch<T extends RouteName, R = any>(
    routeName: T,
    params: RouteParams[T],
    options: RequestInit = {},
): Promise<R> {
    const url = getApiUrl(routeName, params);
    const response = await fetch(url, options);

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
 * (Simple redirect method)
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
        // Use the type-safe API fetch to get wordform metadata
        return await apiFetch(
            RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API,
            { target_language_code, wordform },
            {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            },
        );
    } catch (error) {
        // For 404 errors, return the error response
        // This allows us to handle "invalid word" cases with proper data
        if (error instanceof Error && error.message.includes('404')) {
            const response = await fetch(
                getApiUrl(RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API, 
                    { target_language_code, wordform }
                ),
                {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                }
            );
            return await response.json();
        }
        throw error;
    }
}
