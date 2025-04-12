/**
 * Type definitions for API responses
 */

export interface Language {
    code: string;
    name: string;
}

export interface Sentence {
    id: number;
    target_language_code: string;
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
    target_language_code: string;
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

export interface SearchResult {
    status: 'found' | 'multiple_matches' | 'redirect' | 'invalid' | 'empty_query' | 'error';
    query: string;
    target_language_code: string;
    target_language_name: string;
    data: any; // This will contain different data based on the status
    error?: string;
}

/**
 * Word preview data for tooltips
 * 
 * Response from /api/lang/word/{target_language_code}/{word}/preview
 * Used in EnhancedText component for displaying word information in tooltips
 */
export interface WordPreview {
    // Required fields from the API
    lemma: string;
    translation: string;
    
    // Optional fields that may be present
    etymology?: string | null;
    translations?: string[]; // Some responses use array format
    
    // Debug information (only in development)
    _debug?: {
        url?: string;
        error?: string;
    };
}
