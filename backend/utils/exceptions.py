class AuthenticationRequiredForGenerationError(Exception):
    """Custom exception raised when AI generation is required but the user is not logged in."""

    pass


class DatabaseOverloadedError(Exception):
    """Raised when the connection pool is exhausted and we gave up waiting.

    Deliberately NOT a subclass of `playhouse.pool.MaxConnectionsExceeded`, which
    subclasses `ValueError`. Several handlers catch `ValueError` to turn bad input
    into a 400 (e.g. `sentence_api.ensure_sentence_audio_api`), so raw pool
    exhaustion was being reported to callers as "your request was malformed"
    instead of "the server is over capacity". Translating at the point we give up
    keeps overload distinguishable from user error everywhere downstream.
    """

    pass
