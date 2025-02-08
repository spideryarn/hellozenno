import os


def is_fly_cloud() -> bool:
    """Check if we're running on Fly.io.

    Fly.io sets FLY_APP_NAME environment variable in all deployed applications.
    """
    return os.getenv("FLY_APP_NAME") is not None
