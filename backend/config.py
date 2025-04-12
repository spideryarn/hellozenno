from pathlib import Path
from utils.env_config import (
    is_vercel,
)

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
SOURCEDIR_SLUG_MAX_LENGTH = 100  # Characters allowed in URL slugs
SOURCEFILE_SLUG_MAX_LENGTH = 100  # Characters allowed in URL slugs

DEFAULT_MAX_NEW_WORDS_FOR_UNPROCESSED_SOURCEFILE = 3
DEFAULT_MAX_NEW_PHRASES_FOR_UNPROCESSED_SOURCEFILE = 1
# more than 10 seems to timeout or run out of tokens
DEFAULT_MAX_NEW_WORDS_FOR_PROCESSED_SOURCEFILE = 10
DEFAULT_MAX_NEW_PHRASES_FOR_PROCESSED_SOURCEFILE = 10

# Database pool configuration
# These settings are used across all environments
DB_POOL_CONFIG = {
    "max_connections": 10,  # Reduced from 20 since traffic is light
    "stale_timeout": 600,  # Increased to 10 minutes to keep connections alive longer
    "timeout": 30,  # 30 seconds connection timeout
    "autoconnect": True,
    "thread_safe": True,
}
