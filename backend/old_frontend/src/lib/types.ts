interface Metadata {
  created_at: string | null;
  updated_at: string | null;
}

interface Sentence {
  id: number;
  sentence: string;
  translation: string | null;
  slug: string;
  target_language_code: string;
  has_audio: boolean;
  lemma_words?: string[];
}

export interface SentenceProps {
  sentence: Sentence;
  metadata: Metadata;
  enhanced_sentence_text: string;
}

// Flashcard types
export interface SentenceData {
  id: number;
  slug: string;
  text: string;
  translation: string;
  lemmaWords: string[];
  audioUrl: string;
}

export interface FlashcardState {
  stage: 1 | 2 | 3;  // 1: audio, 2: sentence, 3: translation
  sentence: SentenceData;
  isLoading: boolean;
  error: string | null;
  sourceFilter: {
    type: 'sourcefile' | 'sourcedir' | null;
    slug: string | null;
  };
}

export type FlashcardStage = 1 | 2 | 3;