import os
from pathlib import Path


def is_cloud_run() -> bool:
    """Check if we're running on Google Cloud Run."""
    return os.getenv("K_SERVICE") is not None or os.getenv("GOOGLE_CLOUD_RUN") == "1"


def get_credentials() -> str | None:
    """Get credentials path or None if running on Cloud Run.

    On Cloud Run, we don't need explicit credentials as the service
    automatically uses the service account assigned to the Cloud Run service.
    """
    if is_cloud_run():
        return None
    return os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
