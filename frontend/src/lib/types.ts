/**
 * Type definitions for API responses
 */

/**
 * User profile data returned from the backend API.
 * Matches the Profile.to_dict() output from backend/db_models.py
 */
export interface UserProfile {
    id: number;
    user_id: string;
    target_language_code: string | null;
    admin_granted_at: string | null; // ISO date string
    created_at: string | null; // ISO date string
    updated_at: string | null; // ISO date string
    email?: string; // Added by profile_api.py from auth.users
}

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

/**
 * Entry for example usage in lemmas.
 */
export interface ExampleUsageEntry {
    phrase: string;
    translation: string;
    slug: string;
}

/**
 * Entry for related lemmas (synonyms, antonyms, related words/phrases/idioms).
 * These are simplified Lemma objects used in LemmaCard displays.
 */
export interface RelatedLemmaEntry {
    lemma: string;
    translations?: string[];
    part_of_speech?: string;
    commonality?: number;
    is_complete?: boolean;
}

/**
 * Type for LemmaCard component which can accept either a full Lemma
 * or a simplified RelatedLemmaEntry.
 */
export type LemmaCardData = Lemma | RelatedLemmaEntry;

/**
 * Entry for easily confused lemmas with detailed comparison information.
 * Used in the "Easily Confused With" section of lemma pages.
 */
export interface EasilyConfusedEntry {
    lemma: string;
    translations?: string[];
    part_of_speech?: string;
    commonality?: number;
    is_complete?: boolean;
    explanation?: string;
    example_usage_this_target?: string;
    example_usage_this_source?: string;
    example_usage_this_slug?: string;
    example_usage_other_target?: string;
    example_usage_other_source?: string;
    example_usage_other_slug?: string;
    notes?: string;
    mnemonic?: string;
}

export interface Lemma {
    lemma: string;
    is_complete: boolean;
    part_of_speech: string;
    translations: string[];
    etymology?: string;
    synonyms?: RelatedLemmaEntry[];
    antonyms?: RelatedLemmaEntry[];
    related_words_phrases_idioms?: RelatedLemmaEntry[];
    register?: string;
    commonality?: number | null;
    guessability?: number | null;
    cultural_context?: string;
    mnemonics?: string[];
    example_usage?: ExampleUsageEntry[];
    example_wordforms?: string[];
    easily_confused_with?: EasilyConfusedEntry[];
    // API response may include these additional fields
    generation_in_progress?: boolean;
    authentication_required_for_generation?: boolean;
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

// Base fields common to all SearchResult variants
interface SearchResultBase {
    query: string;
    target_language_code: string;
    target_language_name: string;
}

// Wordform metadata returned when a word is found
export interface SearchWordformMetadata {
    wordform: string;
    lemma?: string | null;
    translations?: string[];
    part_of_speech?: string | null;
    inflection_type?: string | null;
    inflection_types?: string[];
}

export interface SearchResultFound extends SearchResultBase {
    status: 'found';
    data: {
        wordform_metadata: SearchWordformMetadata;
    };
}

export interface SearchResultMultipleMatches extends SearchResultBase {
    status: 'multiple_matches';
    data: {
        search_term: string;
        target_language_results: SearchResultCategory;
        english_results: SearchResultCategory;
    };
}

export interface SearchResultInvalid extends SearchResultBase {
    status: 'invalid';
    data: {
        error: string;
        description?: string;
        wordform: string;
        possible_misspellings?: string[];
    };
}

export interface SearchResultRedirect extends SearchResultBase {
    status: 'redirect';
    data: {
        redirect_to?: string;
        wordform?: string;
    };
}

export interface SearchResultEmptyQuery extends SearchResultBase {
    status: 'empty_query';
    data: Record<string, never>;
}

export interface SearchResultAuthRequired extends SearchResultBase {
    status: 'authentication_required';
    error: string;
    authentication_required_for_generation: true;
    data: Record<string, never>;
}

export interface SearchResultError extends SearchResultBase {
    status: 'error';
    error: string;
    data: Record<string, never>;
}

export type SearchResult =
    | SearchResultFound
    | SearchResultMultipleMatches
    | SearchResultInvalid
    | SearchResultRedirect
    | SearchResultEmptyQuery
    | SearchResultAuthRequired
    | SearchResultError;

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
    inflection_type?: string; // Grammatical information about the wordform
    
    // Debug information (only in development)
    _debug?: {
        url?: string;
        error?: string;
    };
}

/**
 * Learn page types
 * 
 * These interfaces define the API responses for the /api/lang/learn/* endpoints
 * used in the learn page for priority words and flashcard generation.
 */

/**
 * Lemma entry returned from the learn summary API.
 * Contains lemma data with priority scoring metadata.
 */
export interface LearnSummaryLemma {
    lemma: string;
    translations: string[];
    etymology?: string;
    commonality?: number | null;
    guessability?: number | null;
    part_of_speech?: string;
    is_complete?: boolean;
}

/**
 * Meta information from the learn summary API response.
 */
export interface LearnSummaryMeta {
    total_candidates: number;
    returned: number;
    durations?: {
        total_s?: number;
        bulk_fetch_s?: number;
        lemma_warmup_total_s?: number;
        [key: string]: number | undefined;
    };
    partial?: boolean;
    counts?: {
        lemmas_total?: number;
        existing_loaded?: number;
        generated?: number;
        fallback_defaults?: number;
        skipped_due_to_budget?: number;
    };
}

/**
 * Meta information from the learn generate API response.
 */
export interface LearnGenerateMeta {
    reused_count?: number;
    new_count?: number;
    durations?: {
        reuse_s?: number;
        llm_s?: number;
        audio_total_s?: number;
        total_s?: number;
        [key: string]: number | undefined;
    };
    timed_out?: boolean;
    skipped_due_to_timeout?: number;
}

/**
 * Interface for a p-queue-like task queue used for lemma warming
 * and audio prefetch in the learn page.
 */
export interface WarmingQueue {
    add<T>(fn: () => Promise<T>, options?: { priority?: number }): Promise<T>;
    onIdle(): Promise<void>;
}
