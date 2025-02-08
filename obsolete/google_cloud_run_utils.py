import os
from pathlib import Path

# # project ID, i.e. name
# GOOGLE_CLOUD_PROJECT = environ.get("GOOGLE_CLOUD_PROJECT")
# GOOGLE_CLOUD_STORAGE_BUCKET = environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")
# # for Oauth
# GOOGLE_CLIENT_CREDENTIALS = Path(
#     "credentials/241119_google_cloud_oauth_client_secret_732376889523-5qd6h3gm4s1q05cnlskqanf5cceeav7j.apps.googleusercontent.com.json"
# )


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
