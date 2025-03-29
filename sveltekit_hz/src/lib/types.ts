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
