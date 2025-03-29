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
