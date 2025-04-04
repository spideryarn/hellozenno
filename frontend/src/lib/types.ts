/**
 * Type definitions for API responses
 */

export interface Language {
    code: string;
    name: string;
}

export interface Sentence {
    id: number;
    language_code: string;
    text: string;
    translation: string;
    slug: string;
    has_audio: boolean;
    lemma_words?: string[];
}

export interface SentenceMetadata {
    created_at?: string;
    updated_at?: string;
}

export interface Lemma {
    lemma: string;
    is_complete: boolean;
    part_of_speech: string;
    translations: string[];
    etymology?: string;
    synonyms?: any[];
    antonyms?: any[];
    related_words_phrases_idioms?: any[];
    register?: string;
    commonality?: number;
    guessability?: number;
    cultural_context?: string;
    mnemonics?: string[];
    example_usage?: {
        phrase: string;
        translation: string;
        slug: string;
    }[];
    example_wordforms?: string[];
    easily_confused_with?: any[];
}

export interface Wordform {
    wordform: string;
    lemma?: string;
    language_code: string;
    part_of_speech?: string;
    translations: string[];
    inflection_type?: string;
    commonality?: number;
}

export interface Phrase {
    canonical_form: string;
    translations: string[];
    part_of_speech: string;
    slug: string;
    raw_forms: string[];
    difficulty_level?: number;
    register?: string;
    usage_notes?: string;
    created_at?: string;
    updated_at?: string;
}

/**
 * Search result types and interfaces
 */

export interface SearchMatch {
    target_language_wordform: string;
    target_language_lemma?: string;
    part_of_speech?: string;
    english?: string[];
    inflection_type?: string;
    confidence?: number;
}

export interface SearchResultCategory {
    matches: SearchMatch[];
    possible_misspellings?: string[];
}

export interface SearchResults {
    status: 'found' | 'multiple_matches' | 'redirect' | 'invalid';
    target_language_code: string;
    target_language_name: string;
    search_term: string;
    target_language_results?: SearchResultCategory;
    english_results?: SearchResultCategory;
    redirect_to?: string;
    wordform_metadata?: Wordform;
    possible_misspellings?: string[];
    error?: string;
}
