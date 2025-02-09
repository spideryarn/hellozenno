"""Environment configuration module.

Loads environment variables from .env.local and validates them against .env.example.
All environment variables are required and validated using Pydantic types.
"""

from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from pydantic import StrictStr, PositiveInt, SecretStr, TypeAdapter
from typing import Any, TypeVar, Type, Set, cast, Optional

ENV_FILE_EXAMPLE = Path(".env.example")
ENV_FILE_LOCAL = Path(".env.local")
ENV_FILE_TESTING = Path(".env.testing")
ENV_FILE_LOCAL_WITH_FLY_PROXY = Path(".env.local_with_fly_proxy")
ENV_FILE_FLY_CLOUD = Path(".env.fly_cloud")  # TODO we need to create this


logger = logging.getLogger(__name__)

# Track which variables we've processed
_processed_vars: Set[str] = set()

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
    assert env_file.exists(), f"Missing required {env_file}"
    logger.info("Loading environment from %s", env_file)
    # if we're testing, we want to be sure to override the environment variables,
    # so we never accidentally run test code on production
    load_dotenv(env_file, override=is_testing())
    return env_file


def get_env_var(name: str, type_: Any = StrictStr) -> T:
    """Get environment variable with type validation.

    Args:
        name: Name of environment variable
        type_: Pydantic type to validate against (default: StrictStr for non-empty string)

    Returns:
        The validated value with the specified type

    Raises:
        ValueError: If variable is missing or fails validation
    """
    try:
        value = os.environ[name]
        _processed_vars.add(name)

        # Use TypeAdapter for validation
        adapter = TypeAdapter(type_)
        validated = adapter.validate_python(value)

        # Return validated value directly
        return cast(T, validated)
    except KeyError:
        raise ValueError(f"Missing required environment variable: {name}")
    except Exception as e:
        raise ValueError(f"Invalid value for {name}: {e}")


def list_env_example_vars() -> Set[str]:
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


# Load environment on module import
decide_environment_and_load_dotenv_file()

# Database configuration
POSTGRES_DB_NAME = get_env_var("POSTGRES_DB_NAME")  # type: ignore
POSTGRES_DB_USER = get_env_var("POSTGRES_DB_USER")  # type: ignore
POSTGRES_DB_PASSWORD = get_env_var("POSTGRES_DB_PASSWORD", SecretStr)  # type: ignore
POSTGRES_HOST = get_env_var("POSTGRES_HOST")  # type: ignore
POSTGRES_PORT = get_env_var("POSTGRES_PORT", PositiveInt)  # type: ignore

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
required_vars = list_env_example_vars()
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
