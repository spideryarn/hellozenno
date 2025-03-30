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

// Base URL for the Flask API
const API_BASE_URL = "http://localhost:3000";

/**
 * Constructs an API URL based on the provided endpoint
 * Default API is running on localhost:3000 but can be configured with VITE_API_URL environment variable
 *
 * @param endpoint The API endpoint path (should start with a slash)
 * @returns The complete API URL
 */
export function getApiUrl(endpoint: string): string {
    const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:3000";
    return `${apiBaseUrl}${endpoint}`;
}

/**
 * Fetches data from the API with proper error handling
 *
 * @param endpoint The API endpoint path
 * @returns A promise that resolves to the JSON response
 */
export async function fetchFromApi<T>(endpoint: string): Promise<T> {
    const response = await fetch(getApiUrl(endpoint));

    if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
}

/**
 * Fetch all available languages
 */
export async function getLanguages() {
    return fetchFromApi<{ languages: Language[] }>("/api/languages");
}

/**
 * Fetch a sentence by language code and slug
 */
export async function getSentence(languageCode: string, slug: string) {
    return fetchFromApi<
        {
            sentence: Sentence;
            enhanced_sentence_text: string;
            metadata: SentenceMetadata;
        }
    >(
        `/api/language/${languageCode}/sentence/${slug}`,
    );
}

/**
 * Fetch all sentences for a language
 */
export async function getSentencesForLanguage(languageCode: string) {
    return fetchFromApi<Sentence[]>(
        `/api/lang/sentence/${languageCode}/sentences`,
    );
}

/**
 * Fetch all lemmas for a language
 */
export async function getLemmasForLanguage(
    languageCode: string,
    sort: string = "alpha",
) {
    return fetchFromApi<Lemma[]>(
        `/api/lang/lemma/${languageCode}/lemmas?sort=${sort}`,
    );
}

/**
 * Fetch all phrases for a language
 */
export async function getPhrasesForLanguage(
    languageCode: string,
    sort: string = "alpha",
) {
    return fetchFromApi<Phrase[]>(
        `/api/lang/phrase/${languageCode}/phrases?sort=${sort}`,
    );
}

/**
 * Fetch all wordforms for a language
 */
export async function getWordformsForLanguage(
    languageCode: string,
    sort: string = "alpha",
) {
    return fetchFromApi<Wordform[]>(
        `/api/lang/word/${languageCode}/wordforms?sort=${sort}`,
    );
}
