"""Environment configuration module.

Loads environment variables and validates them against .env.example
"""

from dotenv import load_dotenv
import logging
import os
from pathlib import Path

ENV_FILEN_LOCAL = Path(".env.example")
ENV_FILEN_LOCAL = Path(".env.local")

logger = logging.getLogger(__name__)


def validate_env_vars():
    """Validate that all variables in .env.example exist in environment."""
    if not ENV_FILEN_LOCAL.exists():
        logger.warning(".env.example not found - skipping validation")
        return

    # Read required variables from .env.example
    required_vars = set()
    with ENV_FILEN_LOCAL.open() as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Get variable name (everything before =)
            var_name = line.split("=")[0].strip()
            required_vars.add(var_name)

    # Check all required variables exist
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env.local file against .env.example"
        )


# Load environment variables
if ENV_FILEN_LOCAL.exists():
    logger.info("Loading environment from %s", ENV_FILEN_LOCAL)
    load_dotenv(ENV_FILEN_LOCAL)
else:
    logger.warning("%s not found - using environment variables", ENV_FILEN_LOCAL)

# Validate environment variables
validate_env_vars()
