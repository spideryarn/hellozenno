from os import environ
from pathlib import Path
from urllib.parse import urlparse
from fly_cloud_utils import is_fly_cloud

# from google_cloud_run_utils import is_cloud_run

# gets imported by app.py
SECRET_KEY = environ.get("FLASK_SECRET_KEY")
if not SECRET_KEY:
    try:
        from _secrets import FLASK_SECRET_KEY as SECRET_KEY
    except ImportError:
        raise ValueError(
            "FLASK_SECRET_KEY environment variable not set and _secrets.py not found"
        )


SOURCEFILES_DIRN = Path("sourcefiles")


# Database configuration
def is_production():
    """Check if we're running in a production environment (Cloud Run or Fly.io)"""
    # return is_cloud_run()
    return is_fly_cloud()


if is_production():
    # Production uses PostgreSQL
    database_url = environ.get("DATABASE_URL")
    if database_url:
        # Parse the DATABASE_URL from Fly.io
        db_url = urlparse(database_url)
        DB_CONFIG = {
            "ENGINE": "postgresql",
            "NAME": db_url.path[1:],  # Remove leading slash
            "USER": db_url.username,
            "PASSWORD": db_url.password,
            "HOST": db_url.hostname,
            "PORT": db_url.port or 5432,
        }
    else:
        # Fallback to environment variables
        DB_CONFIG = {
            "ENGINE": "postgresql",
            "NAME": environ.get("POSTGRES_DB_NAME", "hz-production"),
            "USER": environ.get("POSTGRES_DB_USER", "postgres"),
            "PASSWORD": environ.get("POSTGRES_DB_PASSWORD"),
            "HOST": environ.get("POSTGRES_HOST", "localhost"),
            "PORT": int(environ.get("POSTGRES_PORT", "5432")),
        }
        if not DB_CONFIG["PASSWORD"]:
            raise ValueError("No database password found in environment variables")
else:
    # Local development uses PostgreSQL too
    from _secrets import (
        POSTGRES_DB_PASSWORD,
        POSTGRES_DB_USER,
        POSTGRES_DB_NAME,
        POSTGRES_HOST,
        POSTGRES_PORT,
    )

    DB_CONFIG = {
        "ENGINE": "postgresql",
        "NAME": environ.get("POSTGRES_DB_NAME", "hellozenno_development"),
        "USER": environ.get("POSTGRES_DB_USER", POSTGRES_DB_USER),
        "PASSWORD": POSTGRES_DB_PASSWORD,
        "HOST": environ.get("POSTGRES_HOST", "localhost"),
        "PORT": int(environ.get("POSTGRES_PORT", "5432")),
    }

# Production uses a different metadata directory
METADATA_DIRN = (
    Path("/app/metadata")
    if is_production()
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

AWS_ACCESS_KEY_ID = "tid_LpfspnVLtmOblMjemDLFHeupE_tYWCKgFUfdoqyrJYUmJvsTjg"
AWS_ENDPOINT_URL_S3 = "https://fly.storage.tigris.dev"
AWS_REGION = "auto"
AWS_SECRET_ACCESS_KEY = (
    "tsec_a8V1OQG_JgCSoENGxPD2ByiDuZ3c0B+WhmXUCJ06RzgaVQTk287P+Wfa_x46TwBjNmz--L"
)
BUCKET_NAME = "hz-storage"
