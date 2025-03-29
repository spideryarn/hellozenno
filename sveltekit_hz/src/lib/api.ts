/**
 * API utility for communicating with the Flask backend
 */

import type { Language, Lemma, Sentence, SentenceMetadata } from "./types";

// Base URL for the Flask API
const API_BASE_URL = "http://localhost:3000";

/**
 * Generic fetch function with error handling
 */
async function fetchFromApi<T>(
    endpoint: string,
    options: RequestInit = {},
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
        });

        if (!response.ok) {
            throw new Error(
                `API error: ${response.status} ${response.statusText}`,
            );
        }

        return await response.json() as T;
    } catch (error) {
        console.error("API request failed:", error);
        throw error;
    }
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
