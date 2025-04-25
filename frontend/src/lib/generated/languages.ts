// Auto-generated from Flask language configuration
/**
 * Interface for a language definition
 */
export interface Language {
  /** Two-letter language code (ISO 639-1) */
  code: string;
  /** Human-readable language name */
  name: string;
}

/**
 * All supported languages in the application.
 * This is auto-generated from backend configuration.
 */
export const LANGUAGES: Language[] = [
  { code: "ar", name: "Arabic" },
  { code: "bn", name: "Bangla" },
  { code: "zh", name: "Chinese" },
  { code: "hr", name: "Croatian" },
  { code: "da", name: "Danish" },
  { code: "nl", name: "Dutch" },
  { code: "fi", name: "Finnish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "el", name: "Greek (modern)" },
  { code: "ha", name: "Hausa" },
  { code: "hi", name: "Hindi" },
  { code: "hu", name: "Hungarian" },
  { code: "id", name: "Indonesian" },
  { code: "it", name: "Italian" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "mr", name: "Marathi" },
  { code: "no", name: "Norwegian" },
  { code: "pl", name: "Polish" },
  { code: "pt", name: "Portuguese" },
  { code: "pa", name: "Punjabi" },
  { code: "es", name: "Spanish" },
  { code: "sw", name: "Swahili" },
  { code: "sv", name: "Swedish" },
  { code: "tl", name: "Tagalog" },
  { code: "ta", name: "Tamil" },
  { code: "te", name: "Telugu" },
  { code: "th", name: "Thai" },
  { code: "tr", name: "Turkish" },
  { code: "ur", name: "Urdu" },
  { code: "vi", name: "Vietnamese" },
];

/**
 * Map of language codes to language names for quick lookups.
 */
export const LANGUAGE_NAMES: Record<string, string> = {
  "ar": "Arabic",
  "bn": "Bangla",
  "zh": "Chinese",
  "hr": "Croatian",
  "da": "Danish",
  "nl": "Dutch",
  "fi": "Finnish",
  "fr": "French",
  "de": "German",
  "el": "Greek (modern)",
  "ha": "Hausa",
  "hi": "Hindi",
  "hu": "Hungarian",
  "id": "Indonesian",
  "it": "Italian",
  "ja": "Japanese",
  "ko": "Korean",
  "mr": "Marathi",
  "no": "Norwegian",
  "pl": "Polish",
  "pt": "Portuguese",
  "pa": "Punjabi",
  "es": "Spanish",
  "sw": "Swahili",
  "sv": "Swedish",
  "tl": "Tagalog",
  "ta": "Tamil",
  "te": "Telugu",
  "th": "Thai",
  "tr": "Turkish",
  "ur": "Urdu",
  "vi": "Vietnamese",
};

/**
 * Get a language name from a language code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language name, or the code if not found
 */
export function getLanguageName(target_language_code: string): string {
  return LANGUAGE_NAMES[target_language_code] || target_language_code;
}

/**
 * Find a language by its code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language object, or undefined if not found
 */
export function findLanguageByCode(target_language_code: string): Language | undefined {
  return LANGUAGES.find(lang => lang.code === target_language_code);
}
