interface Metadata {
  created_at: string | null;
  updated_at: string | null;
}

interface Sentence {
  id: number;
  sentence: string;
  translation: string | null;
  slug: string;
  language_code: string;
  has_audio: boolean;
  lemma_words?: string[];
}

export interface SentenceProps {
  sentence: Sentence;
  metadata: Metadata;
  target_language_code: string;
  target_language_name: string;
  enhanced_sentence_text: string;
} 