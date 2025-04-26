"""Environment configuration module.

Loads environment variables from .env.local and validates them against .env.example.
All environment variables are required and validated using Pydantic types.
"""

from dotenv import load_dotenv
from gjdutils.env import get_env_var, list_env_example_vars
import logging
import os
from pathlib import Path
from pydantic import SecretStr
from typing import TypeVar, Type

# Update paths to point to the project root directory
PROJECT_ROOT = Path(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
ENV_FILE_EXAMPLE = PROJECT_ROOT / ".env.example"
ENV_FILE_LOCAL = PROJECT_ROOT / ".env.local"
ENV_FILE_TESTING = PROJECT_ROOT / ".env.testing"
ENV_FILE_PROD = PROJECT_ROOT / ".env.prod"


logger = logging.getLogger(__name__)

# Track which variables we've processed
_processed_vars: set[str] = set()

T = TypeVar("T")


def get_env_var_and_track(var_name: str, type_adapter: Type[T] | None = None) -> T:
    """Wrapper around gjdutils.env.get_env_var that tracks processed variables.

    Args:
        var_name: Name of environment variable to get
        type_adapter: Optional Pydantic type to validate value against

    Returns:
        The environment variable value, validated against type_adapter if provided
    """
    value = get_env_var(var_name, type_adapter)
    _processed_vars.add(var_name)
    return value


def is_testing() -> bool:
    """Check if we're running in a test environment.

    This checks for the PYTEST_CURRENT_TEST environment variable which pytest sets
    during test runs.
    """
    return "PYTEST_CURRENT_TEST" in os.environ


def is_vercel() -> bool:
    """Check if we're running on Vercel.

    Vercel sets VERCEL environment variable in all deployed applications.
    """
    vercel = os.getenv("VERCEL", "0").strip()
    assert vercel is None or vercel in [
        "0",
        "1",
    ], f"VERCEL must be None, '0', or '1', got '{vercel}' ({type(vercel)})"
    return vercel == "1"


def is_local_to_prod() -> bool:
    """Check if we're connecting to production database from local machine."""
    local_to_prod = os.getenv("USE_LOCAL_TO_PROD", "0").strip()
    if is_vercel():
        return False
    assert local_to_prod is None or local_to_prod in [
        "0",
        "1",
    ], f"USE_LOCAL_TO_PROD must be '0' or '1', 'got '{local_to_prod}', {type(local_to_prod)}"
    return local_to_prod == "1"


def decide_environment_file() -> Path:
    """Choose which .env file to load based on environment.

    Returns:
        Optional[Path]: Path to the .env file to load, or None for production
    """
    # these should be mutually exclusive
    assert (
        sum([is_testing(), is_vercel(), is_local_to_prod()]) <= 1
    ), "Testing, production, Vercel, and local-to-prod should be mutually exclusive"

    if is_testing():
        return ENV_FILE_TESTING
    if is_vercel():
        return ENV_FILE_PROD
    if is_local_to_prod():
        raise Exception("Local-to-prod is not supported in this script")
    return ENV_FILE_LOCAL


def decide_environment_and_load_dotenv_file():
    """Load environment variables from the appropriate .env file.

    The environment file is selected based on the current environment:
    - test: .env.testing (required)
    - prod: no file (we don't send up `.env.prod` to prod - instead we set environment variables during deploy)
    - local_to_prod: .env.local_to_prod (required)
    - local: .env.local (required)

    Raises:
        AssertionError: If required environment file is missing
    """
    env_file = decide_environment_file()
    logger.info("Using environment file: %s", env_file)
    # we don't want to send the .env file up to production, so don't
    # require it to be there it's there. we're setting all the
    # production environment variables with `set_secrets_for_fly_cloud.sh`
    if env_file == ENV_FILE_PROD:
        return None
    assert env_file.exists(), f"Missing required {env_file}"
    logger.info("Loading environment from %s", env_file)
    # if we're testing, we want to be sure to override the environment variables,
    # so we never accidentally run test code on production
    load_dotenv(env_file, override=is_testing())
    return env_file


# Load environment on module import
env_file = decide_environment_and_load_dotenv_file()

# Database configuration
DATABASE_URL = get_env_var_and_track("DATABASE_URL", SecretStr)  # type: ignore

# API Keys
CLAUDE_API_KEY = get_env_var_and_track("CLAUDE_API_KEY", SecretStr)
OPENAI_API_KEY = get_env_var_and_track("OPENAI_API_KEY", SecretStr)
ELEVENLABS_API_KEY = get_env_var_and_track("ELEVENLABS_API_KEY", SecretStr)

# Flask configuration
FLASK_SECRET_KEY = get_env_var_and_track("FLASK_SECRET_KEY", SecretStr).get_secret_value().strip()  # type: ignore

# Local to prod configuration
USE_LOCAL_TO_PROD = get_env_var_and_track("USE_LOCAL_TO_PROD", int)  # type: ignore

# Supabase configuration
SUPABASE_JWT_SECRET = get_env_var_and_track("SUPABASE_JWT_SECRET", SecretStr)  # type: ignore

VITE_FRONTEND_URL = get_env_var_and_track("VITE_FRONTEND_URL", str)

# # Validate we processed all required variables
# if env_file == ENV_FILE_LOCAL:
#     required_vars = list_env_example_vars(ENV_FILE_EXAMPLE)
#     unprocessed = required_vars - _processed_vars
#     if unprocessed:
#         raise ValueError(
#             f"Variables in .env.example not processed: {', '.join(sorted(unprocessed))}"
#         )

#     unused = _processed_vars - required_vars
#     if unused:
#         logger.warning(
#             "Processing variables not in .env.example: %s", ", ".join(sorted(unused))
#         )
