"""Environment configuration module.

Loads environment variables from .env.local and validates them against .env.example.
All environment variables are required and validated using Pydantic types.
"""

from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from pydantic import StrictStr, PositiveInt, SecretStr
from typing import Any, TypeVar, Type, Set

ENV_FILE_EXAMPLE = Path(".env.example")
ENV_FILE_LOCAL = Path(".env.local")

logger = logging.getLogger(__name__)

# Track which variables we've processed
_processed_vars: Set[str] = set()


def getenv(name: str, type_=StrictStr) -> Any:
    """Get environment variable with type validation.

    Args:
        name: Name of environment variable
        type_: Pydantic type to validate against (default: StrictStr for non-empty string)

    Raises:
        ValueError: If variable is missing or fails validation
    """
    try:
        value = os.environ[name]
        _processed_vars.add(name)
        validated = type_(value)
        return (
            validated.get_secret_value()
            if isinstance(validated, SecretStr)
            else validated
        )
    except KeyError:
        raise ValueError(f"Missing required environment variable: {name}")
    except Exception as e:
        raise ValueError(f"Invalid value for {name}: {e}")


def get_required_vars_from_example() -> Set[str]:
    """Get set of required variables from .env.example."""
    assert ENV_FILE_EXAMPLE.exists(), "Missing .env.example file"

    required_vars = set()
    with ENV_FILE_EXAMPLE.open() as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Get variable name (everything before =)
            var_name = line.split("=")[0].strip()
            required_vars.add(var_name)

    return required_vars


# Load environment variables
if ENV_FILE_LOCAL.exists():
    logger.info("Loading environment from %s", ENV_FILE_LOCAL)
    load_dotenv(ENV_FILE_LOCAL)
else:
    logger.warning("%s not found - using environment variables", ENV_FILE_LOCAL)

# Get required variables before we start processing
required_vars = get_required_vars_from_example()

# Database configuration
POSTGRES_DB_NAME = getenv("POSTGRES_DB_NAME")
POSTGRES_DB_USER = getenv("POSTGRES_DB_USER")
POSTGRES_DB_PASSWORD = getenv("POSTGRES_DB_PASSWORD", SecretStr)
POSTGRES_HOST = getenv("POSTGRES_HOST")
POSTGRES_PORT = getenv("POSTGRES_PORT", PositiveInt)

# API Keys
CLAUDE_API_KEY = getenv("CLAUDE_API_KEY", SecretStr)
OPENAI_API_KEY = getenv("OPENAI_API_KEY", SecretStr)
ELEVENLABS_API_KEY = getenv("ELEVENLABS_API_KEY", SecretStr)

# Flask configuration
FLASK_SECRET_KEY = getenv("FLASK_SECRET_KEY", SecretStr)

# Validate we processed all required variables
unprocessed = required_vars - _processed_vars
if unprocessed:
    raise ValueError(
        f"Variables in .env.example not processed: {', '.join(sorted(unprocessed))}"
    )

unused = _processed_vars - required_vars
if unused:
    logger.warning(
        "Processing variables not in .env.example: %s", ", ".join(sorted(unused))
    )
