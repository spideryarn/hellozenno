export interface Sourcedir {
    id: number;
    path: string;
    slug: string;
    target_language_code: string; // This is kept as target_language_code for backward compatibility
}

export interface Sourcefile {
    id: number;
    filename: string;
    slug: string;
    description: string | null;
    sourcefile_type: "text" | "image" | "audio" | "youtube_audio";
    text_target: string | null;
    text_english: string | null;
    has_audio: boolean;
    has_image: boolean;
    enhanced_text?: string | null;
}

export interface Metadata {
    created_at: string;
    updated_at: string;
    image_processing?: {
        original_size: number;
        final_size: number;
        was_resized: boolean;
    };
}

export interface Navigation {
    current_position: number;
    total_files: number;
    is_first: boolean;
    is_last: boolean;
    prev_slug?: string;
    next_slug?: string;
    first_slug?: string;
    last_slug?: string;
    sourcedir_path?: string;
    prev_filename?: string;
    next_filename?: string;
    first_filename?: string;
    last_filename?: string;
}

export interface Stats {
    wordforms_count: number;
    phrases_count: number;
    already_processed: boolean;
}

export interface Wordform {
    id: number;
    target_language_code: string;
    wordform: string;
    lemma: string;
    frequency: number;
    source: string;
    notes: string | null;
    translation: string | null;
    part_of_speech: string | null;
}

export interface Phrase {
    id: number;
    target_language_code: string;
    phrase: string;
    translation: string | null;
    notes: string | null;
}

export interface SourcefileAPIResponse {
    success: boolean;
    sourcefile: Sourcefile;
    sourcedir: Sourcedir;
    metadata: Metadata;
    stats: Stats;
}

export interface SourcefileTextAPIResponse {
    success: boolean;
    sourcefile: Sourcefile;
    sourcedir: Sourcedir;
    metadata: Metadata;
    navigation: Navigation;
    stats: Stats;
}

export interface SourcefileWordsAPIResponse {
    success: boolean;
    wordforms: Wordform[];
}

export interface SourcefilePhrasesAPIResponse {
    success: boolean;
    phrases: Phrase[];
}
