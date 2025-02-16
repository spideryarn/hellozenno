"""Environment configuration module.

Loads environment variables from .env.local and validates them against .env.example.
All environment variables are required and validated using Pydantic types.
"""

from dotenv import load_dotenv
from gjdutils.env import get_env_var, list_env_example_vars
import logging
import os
from pathlib import Path
from pydantic import StrictStr, PositiveInt, SecretStr, TypeAdapter
from typing import Any, TypeVar, Type, cast, Optional

ENV_FILE_EXAMPLE = Path(".env.example")
ENV_FILE_LOCAL = Path(".env.local")
ENV_FILE_TESTING = Path(".env.testing")
ENV_FILE_LOCAL_WITH_FLY_PROXY = Path(".env.local_with_fly_proxy")
ENV_FILE_FLY_CLOUD = Path(".env.fly_cloud")  # TODO we need to create this


logger = logging.getLogger(__name__)

# Track which variables we've processed
_processed_vars: set[str] = set()

T = TypeVar("T")


def is_testing() -> bool:
    """Check if we're running in a test environment.

    This checks for the PYTEST_CURRENT_TEST environment variable which pytest sets
    during test runs.
    """
    return "PYTEST_CURRENT_TEST" in os.environ


def is_fly_cloud() -> bool:
    """Check if we're running on Fly.io.

    Fly.io sets FLY_APP_NAME environment variable in all deployed applications.
    """
    return os.getenv("FLY_APP_NAME") is not None


def is_local_to_fly_proxy() -> bool:
    """Check if we're connecting to Fly.io Postgres from local machine via proxy."""
    local_to_fly_proxy = os.getenv("USE_FLY_POSTGRES_FROM_LOCAL_PROXY")
    if is_fly_cloud():
        return False
    assert local_to_fly_proxy is None or local_to_fly_proxy in ["0", "1"]
    return local_to_fly_proxy == "1"


def decide_environment_file() -> Path:
    """Choose which .env file to load based on environment.

    Returns:
        Optional[Path]: Path to the .env file to load, or None for Fly.io production
    """
    # these should be mutually exclusive
    assert (
        sum([is_testing(), is_fly_cloud(), is_local_to_fly_proxy()]) <= 1
    ), "Testing, fly-cloud and local-with-fly-proxy should be mutually exclusive"

    if is_testing():
        return ENV_FILE_TESTING
    if is_fly_cloud():
        return ENV_FILE_FLY_CLOUD
    if is_local_to_fly_proxy():
        return ENV_FILE_LOCAL_WITH_FLY_PROXY
    return ENV_FILE_LOCAL


def decide_environment_and_load_dotenv_file():
    """Load environment variables from the appropriate .env file.

    The environment file is selected based on the current environment:
    - test: .env.testing (required)
    - fly: no file (uses environment variables)
    - local_with_fly_proxy: .env.local_with_fly_proxy (required)
    - local: .env.local (required)

    Raises:
        AssertionError: If required environment file is missing
    """
    env_file = decide_environment_file()
    # we don't want to send the .env file up to production, so don't
    # require it to be there it's there. we're setting all the
    # production environment variables with `set_secrets_for_fly_cloud.sh`
    if env_file == ENV_FILE_FLY_CLOUD:
        return None
    assert env_file.exists(), f"Missing required {env_file}"
    logger.info("Loading environment from %s", env_file)
    # if we're testing, we want to be sure to override the environment variables,
    # so we never accidentally run test code on production
    load_dotenv(env_file, override=is_testing())
    return env_file


# Load environment on module import
decide_environment_and_load_dotenv_file()

# Database configuration
DATABASE_URL = get_env_var("DATABASE_URL", SecretStr)  # type: ignore

# API Keys
CLAUDE_API_KEY = get_env_var("CLAUDE_API_KEY", SecretStr)
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY", SecretStr)
ELEVENLABS_API_KEY = get_env_var("ELEVENLABS_API_KEY", SecretStr)

# Flask configuration
FLASK_SECRET_KEY = get_env_var("FLASK_SECRET_KEY", SecretStr).get_secret_value()  # type: ignore

# Proxy configuration
USE_FLY_POSTGRES_FROM_LOCAL_PROXY = get_env_var("USE_FLY_POSTGRES_FROM_LOCAL_PROXY")  # type: ignore

# Validate we processed all required variables
# Get required variables before we start processing
required_vars = list_env_example_vars(ENV_FILE_EXAMPLE)
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
