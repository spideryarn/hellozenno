from pathlib import Path
from env_config import (
    is_fly_cloud,
)


SOURCEFILES_DIRN = Path("sourcefiles")

# Production uses a different metadata directory
METADATA_DIRN = (
    Path("/app/metadata")
    if is_fly_cloud()
    else Path(
        "/Users/greg/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/Greek learning/hellozenno"
    )
)

# Language configuration
LANGUAGE_LEVEL = "B1"  # CEFR level for language learning

# see lang_utils.py
# SUPPORTED_LANGUAGES = None  # None for all languages
SUPPORTED_LANGUAGES = set(
    [
        "ar",
        "de",
        "fr",
        "el",
        "es",
        "fi",
        "it",
        "zh",
    ]
)

LANGUAGE_NAME_OVERRIDES = {
    # because Pycountry cumbersomely calls it "Modern Greek (1453-)"
    "el": "Greek",
}

# Supported file extensions for source files
SOURCE_EXTENSIONS = {
    # ".pdf",
    # ".txt",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
}

# Add audio extensions
AUDIO_SOURCE_EXTENSIONS = {".mp3"}
SOURCE_EXTENSIONS.update(AUDIO_SOURCE_EXTENSIONS)

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE_UPLOAD_ALLOWED = 20 * 1024 * 1024  # 20MB
MAX_IMAGE_SIZE_FOR_STORAGE = 4 * 1024 * 1024  # 4MB

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


# Database pool configuration
# These settings are used across all environments
DB_POOL_CONFIG = {
    "max_connections": 20,  # Keep below soft limit
    "stale_timeout": 300,  # 5 minutes
    "timeout": 30,  # 30 seconds connection timeout
    "autoconnect": True,
    "thread_safe": True,
}
