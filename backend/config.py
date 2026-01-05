from utils.types import LanguageLevel


# Language configuration
DEFAULT_LANGUAGE_LEVEL: LanguageLevel = "B1"  # CEFR level for language learning

# see lang_utils.py
# SUPPORTED_LANGUAGES = None  # None for all languages. gets re-sorted by language name
# ordered by total speakers: https://en.wikipedia.org/wiki/List_of_languages_by_total_number_of_speakers
SUPPORTED_LANGUAGES = set(
    [
        # English
        "zh",  # Chinese
        "hi",  # Hindi
        "es",  # Spanish
        "ar",  # Arabic
        "fr",  # French
        "bn",  # Bengali
        "pt",  # Portuguese
        # Russian
        "id",  # Indonesian
        "ur",  # Urdu
        "de",  # German
        "ja",  # Japanese
        # pcm for Nigerian Pidgin - doesn't have 2-digit code
        "mr",  # Marathi
        "vi",  # Vietnamese
        "te",  # Telugu
        "ha",  # Hausa
        "tr",  # Turkish
        "pa",  # Punjabi
        "sw",  # Swahili
        "tl",  # Tagalog
        "ta",  # Tamil
        "ko",  # Korean
        "th",  # Thai
        "it",  # Italian
        # ...
        "el",  # Greek
        "fi",  # Finnish
        "sv",  # Swedish
        "no",  # Norwegian
        "da",  # Danish
        "nl",  # Dutch
        "pl",  # Polish
        "hu",  # Hungarian
        "hr",  # Croatian
    ]
)

LANGUAGE_NAME_OVERRIDES = {
    # because Pycountry cumbersomely calls it "Modern Greek (1453-)"
    "el": "Greek (modern)",
    "pa": "Punjabi",
    "sw": "Swahili",
}

# Supported file extensions for source files
SOURCE_IMAGE_EXTENSIONS = {
    # ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
}

# Add text extensions
TEXT_SOURCE_EXTENSIONS = {".txt", ".md"}

# Add audio extensions
AUDIO_SOURCE_EXTENSIONS = {".mp3"}

# Combine all extensions
SOURCE_EXTENSIONS = SOURCE_IMAGE_EXTENSIONS.copy()
SOURCE_EXTENSIONS.update(AUDIO_SOURCE_EXTENSIONS)
SOURCE_EXTENSIONS.update(TEXT_SOURCE_EXTENSIONS)

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE_UPLOAD_ALLOWED = 20 * 1024 * 1024  # 20MB
MAX_IMAGE_SIZE_FOR_STORAGE = 4 * 1024 * 1024  # 4MB

# Text-specific size limits
# ~10k words with formatting in any language should be under 1MB
MAX_TEXT_SIZE_UPLOAD_ALLOWED = 1 * 1024 * 1024  # 1MB

# Audio-specific size limits
# 60 min medium quality MP3 @ 128kbps = ~54MB
MAX_AUDIO_SIZE_UPLOAD_ALLOWED = 60 * 1024 * 1024  # 60MB
MAX_AUDIO_SIZE_FOR_STORAGE = MAX_AUDIO_SIZE_UPLOAD_ALLOWED  # Store full audio for now

# Valid sourcefile types
VALID_SOURCEFILE_TYPES = {
    "text",  # Direct text input
    "image",  # Uploaded images (OCR processed)
    "audio",  # Uploaded audio files
    "youtube_audio",  # YouTube video audio downloads
}

MAX_NUMBER_UPLOAD_FILES = 20  # Maximum number of files that can be uploaded at once

# Maximum length for slugs
SOURCEDIR_SLUG_MAX_LENGTH = 1024  # Characters allowed in URL slugs
SOURCEFILE_SLUG_MAX_LENGTH = 1024  # Characters allowed in URL slugs

# Maximum new words and phrases per processing run
DEFAULT_MAX_NEW_WORDS_PER_PROCESSING = 8
DEFAULT_MAX_NEW_PHRASES_PER_PROCESSING = 1

# Database pool configuration
# These settings are used across all environments
DB_POOL_CONFIG = {
    # Slightly increase pool headroom to tolerate brief spikes while
    # audio generation runs in parallel (we keep DB windows short elsewhere)
    "max_connections": 14,
    "stale_timeout": 600,
    "timeout": 30,
    "autoconnect": True,
    "thread_safe": True,
}

# Segmentation and recognition defaults (can be overridden via environment vars)
# - These provide code-based defaults so we don't depend on Vercel env configuration.
# - Env overrides (if set) still take precedence, e.g. SEGMENTATION_TH, SEGMENTATION_DEFAULT.
SEGMENTATION_DEFAULT: str = "naive"  # Global default when no per-language override
SEGMENTATION_PER_LANG_DEFAULTS: dict[str, str] = {
    "th": "pythainlp",  # Prefer PyThaiNLP for Thai when ICU is unavailable
    # Add more language-specific defaults if needed, e.g. "zh": "jieba"
}

# Known-word fast path (Aho–Corasick) default. Env RECOGNITION_KNOWN_WORD_SEARCH overrides when provided.
RECOGNITION_KNOWN_WORD_SEARCH_DEFAULT: bool = True

# Thai tokenizer engine default for PyThaiNLP when no env PYTHAINLP_ENGINE is provided
PYTHAINLP_ENGINE_DEFAULT: str = "newmm"

# Text-to-speech voices
# Centralized pool used for both sentences and lemma pronunciations
ELEVENLABS_VOICE_POOL: list[str] = [
    "Adam",
    "Alice",
    "Bill",
    "Brian",
    "Callum",
    "Charlie",
    "Chris",
    "Daniel",
    "Eric",
    "George",
    "Harry",
    "Jessica",
    "Laura",
    "Liam",
    "Lily",
    "Matilda",
    "River",
    "Roger",
    "Sarah",
    "Will",
]

# Deterministic default TTS voice configuration
# Global default voice used when no per-language override is specified
# Number of distinct audio samples to store per lemma (server default)
LEMMA_AUDIO_SAMPLES: int = 3

# Number of distinct audio samples to store per sentence (server default)
SENTENCE_AUDIO_SAMPLES: int = 3

# Auto-generation policy: public never auto-generates; authenticated may auto-generate 1 sample
# TODO remove this. we don't ever want to allow non-logged-in users to be able to generate
PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES: int = 1
